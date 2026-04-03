from __future__ import annotations

import argparse
import time
from typing import Any

import requests

from common import (
    append_section,
    ds_password_fallback_error,
    dump_csv_rows,
    dump_json_report,
    dump_text_report,
    resolve_ds_password,
    stats_block_lines,
    summarize_ms,
)


DEFAULT_DS_EMAIL = "s312192@studenti.polito.it"
DEFAULT_APPLICATION_ID = "com.smartotum.smartotum-camera-manager"
DEFAULT_CONSENT_CONTENT = "Consent to Record Video Footage from Smart Home Cameras"


def build_api_base(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/api"):
        return normalized
    return f"{normalized}/api"


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected_status: int | tuple[int, ...] = 200,
    **kwargs: Any,
) -> Any:
    response = session.request(method, url, timeout=30, **kwargs)
    allowed = (
        expected_status
        if isinstance(expected_status, tuple)
        else (expected_status,)
    )
    if response.status_code not in allowed:
        raise RuntimeError(
            f"{method} {url} failed with {response.status_code}: {response.text[:400]}"
        )
    if not response.content:
        return None
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()
    return response.text


def login(session: requests.Session, api_base: str, email: str, password: str) -> None:
    request_json(
        session,
        "POST",
        f"{api_base}/auth/login",
        expected_status=200,
        json={"email": email, "password": password},
    )


def refresh_testing_snapshot(session: requests.Session, api_base: str) -> None:
    request_json(session, "POST", f"{api_base}/homes/refresh", expected_status=(200, 202))
    request_json(session, "POST", f"{api_base}/applications/refresh", expected_status=200)


def get_home_uuid(session: requests.Session, api_base: str, requested_home_uuid: str | None) -> str:
    if requested_home_uuid:
        return requested_home_uuid
    homes = request_json(session, "GET", f"{api_base}/homes", expected_status=200)
    if not homes:
        raise RuntimeError("No homes available for the authenticated data subject")
    return str(homes[0]["uuid"])


def list_installed_apps(session: requests.Session, api_base: str, home_uuid: str) -> list[dict[str, Any]]:
    return request_json(
        session,
        "GET",
        f"{api_base}/applications/home/{home_uuid}",
        expected_status=200,
    )


def get_consent_state(
    session: requests.Session,
    api_base: str,
    home_uuid: str,
    application_uuid: str,
) -> list[dict[str, Any]]:
    return request_json(
        session,
        "GET",
        f"{api_base}/consents/home/{home_uuid}/application/{application_uuid}",
        expected_status=200,
    )


def get_target_application(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
    application_id: str,
) -> dict[str, Any]:
    installed_apps = list_installed_apps(session, api_base, home_uuid)
    if not installed_apps:
        raise RuntimeError(f"No installed applications found in home {home_uuid}")

    for item in installed_apps:
        application_name = str(item["application"].get("name") or "")
        if application_name == application_id:
            return item

    raise RuntimeError(
        f"Installed application {application_id!r} not found in home {home_uuid}"
    )


def get_target_consent(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
    application_item: dict[str, Any],
    application_id: str,
    consent_content: str,
) -> dict[str, Any]:
    application_uuid = str(application_item["application"]["uuid"])
    consents = get_consent_state(session, api_base, home_uuid, application_uuid)

    for consent in consents:
        current_consent_content = str(consent.get("content") or "")
        if current_consent_content == consent_content and consent.get("sifis_action_id"):
            return consent

    raise RuntimeError(
        "Could not find the pinned consent with a non-null sifis_action_id "
        f"inside application {application_id!r}: {consent_content!r}"
    )


def grant_consent(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
    application_uuid: str,
    consent_uuid: str,
) -> None:
    request_json(
        session,
        "PUT",
        f"{api_base}/consents/home/{home_uuid}/application/{application_uuid}",
        expected_status=204,
        json={"selected_consents": [consent_uuid]},
    )


def withdraw_consent(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
    application_uuid: str,
    consent_uuid: str,
) -> dict[str, Any]:
    return request_json(
        session,
        "POST",
        f"{api_base}/requests/submit",
        expected_status=201,
        json={
            "right_type": "WITHDRAW_CONSENT",
            "additional_information": "Automated latency benchmark withdrawal",
            "smart_home_uuid": home_uuid,
            "application_uuid": application_uuid,
            "selected_consents": [consent_uuid],
        },
    )


def list_privacy_rules(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
) -> list[dict[str, Any]]:
    return request_json(
        session,
        "GET",
        f"{api_base}/dht/homes/{home_uuid}/topic_name/privacy_rule",
        expected_status=200,
    )


def rule_uuid_set(rules: list[dict[str, Any]]) -> set[str]:
    return {str(item["topic_uuid"]) for item in rules}


def wait_for_new_rules(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
    baseline_rule_uuids: set[str],
    timeout_s: float,
    poll_interval_s: float,
) -> tuple[set[str], list[dict[str, Any]]]:
    deadline = time.monotonic() + timeout_s
    latest_rules: list[dict[str, Any]] = []

    while time.monotonic() < deadline:
        latest_rules = list_privacy_rules(session, api_base, home_uuid=home_uuid)
        new_rule_uuids = rule_uuid_set(latest_rules) - baseline_rule_uuids
        if new_rule_uuids:
            return new_rule_uuids, latest_rules
        time.sleep(poll_interval_s)

    raise TimeoutError(
        f"Timed out after {timeout_s:.1f}s waiting for new privacy_rule entries on DHT"
    )


def wait_until_rules_removed(
    session: requests.Session,
    api_base: str,
    *,
    home_uuid: str,
    target_rule_uuids: set[str],
    timeout_s: float,
    poll_interval_s: float,
) -> None:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        current_rule_uuids = rule_uuid_set(
            list_privacy_rules(session, api_base, home_uuid=home_uuid)
        )
        if not (current_rule_uuids & target_rule_uuids):
            return
        time.sleep(poll_interval_s)

    raise TimeoutError(
        f"Timed out after {timeout_s:.1f}s waiting for cleanup of DHT rules {sorted(target_rule_uuids)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark policy propagation latency from consent withdrawal submission "
            "to deny rule visibility on the Smartotum DHT proxy endpoint."
        )
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:5050")
    parser.add_argument("--ds-email", default=DEFAULT_DS_EMAIL)
    parser.add_argument(
        "--ds-password",
        help=(
            "Real Smartotum password for the Data Subject. If omitted, the script tries "
            "the testing-only fallback password, which works only with FLASK_ENV=testing."
        ),
    )
    parser.add_argument(
        "--application-id",
        default=DEFAULT_APPLICATION_ID,
        help=(
            "Installed application identifier to benchmark, matched against the application "
            "name returned by /api/applications/home/<home_uuid>."
        ),
    )
    parser.add_argument(
        "--consent-content",
        default=DEFAULT_CONSENT_CONTENT,
        help="Consent content string to withdraw inside the selected application.",
    )
    parser.add_argument("--home-uuid")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--settle-timeout", type=float, default=10.0)
    parser.add_argument("--poll-interval", type=float, default=0.2)
    parser.add_argument("--skip-refresh", action="store_true")
    parser.add_argument("--keep-withdrawn-state", action="store_true")
    parser.add_argument("--json-out")
    parser.add_argument("--csv-out")
    parser.add_argument("--txt-out")
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")
    if args.warmup < 0:
        raise SystemExit("--warmup must be >= 0")

    terminal_lines: list[str] = []

    def log(message: str = "") -> None:
        print(message)
        terminal_lines.append(message)

    api_base = build_api_base(args.base_url)
    session = requests.Session()
    ds_password, used_testing_fallback = resolve_ds_password(args.ds_password)
    try:
        login(session, api_base, args.ds_email, ds_password)
    except RuntimeError as exc:
        if used_testing_fallback:
            raise SystemExit(
                ds_password_fallback_error("benchmark_withdraw_latency.py")
            ) from exc
        raise
    if used_testing_fallback:
        log("No --ds-password provided; using the testing-only Data Subject password fallback.")

    if not args.skip_refresh:
        refresh_testing_snapshot(session, api_base)

    home_uuid = get_home_uuid(session, api_base, args.home_uuid)
    application_item = get_target_application(
        session,
        api_base,
        home_uuid=home_uuid,
        application_id=args.application_id,
    )
    consent = get_target_consent(
        session,
        api_base,
        home_uuid=home_uuid,
        application_item=application_item,
        application_id=args.application_id,
        consent_content=args.consent_content,
    )
    application_uuid = str(application_item["application"]["uuid"])
    application_name = str(application_item["application"].get("name") or "")
    application_title = str(application_item["application"].get("title") or "")
    consent_uuid = str(consent["uuid"])
    consent_content = str(consent.get("content") or "")

    log(f"Home UUID       : {home_uuid}")
    log(f"Application Name: {application_name}")
    log(f"Application Title: {application_title}")
    log(f"Application UUID: {application_uuid}")
    log(f"Consent UUID    : {consent_uuid}")
    log(f"Consent Content : {consent_content}")

    run_count = args.warmup + args.iterations
    measured_rows: list[dict[str, Any]] = []

    for run_index in range(run_count):
        current_state = get_consent_state(session, api_base, home_uuid, application_uuid)
        matching = next((item for item in current_state if str(item["uuid"]) == consent_uuid), None)
        if matching is None:
            raise RuntimeError(f"Consent {consent_uuid} no longer exists in application {application_uuid}")
        if matching.get("given") is not True:
            grant_consent(
                session,
                api_base,
                home_uuid=home_uuid,
                application_uuid=application_uuid,
                consent_uuid=consent_uuid,
            )

        baseline_rules = list_privacy_rules(session, api_base, home_uuid=home_uuid)
        baseline_rule_uuids = rule_uuid_set(baseline_rules)

        t0 = time.perf_counter_ns()
        created_request = withdraw_consent(
            session,
            api_base,
            home_uuid=home_uuid,
            application_uuid=application_uuid,
            consent_uuid=consent_uuid,
        )
        submit_done_ns = time.perf_counter_ns()
        new_rule_uuids, latest_rules = wait_for_new_rules(
            session,
            api_base,
            home_uuid=home_uuid,
            baseline_rule_uuids=baseline_rule_uuids,
            timeout_s=args.settle_timeout,
            poll_interval_s=args.poll_interval,
        )
        first_seen_ns = time.perf_counter_ns()

        submit_http_ms = (submit_done_ns - t0) / 1_000_000.0
        first_seen_ms = (first_seen_ns - t0) / 1_000_000.0

        row = {
            "run_index": run_index + 1,
            "phase": "warmup" if run_index < args.warmup else "measured",
            "request_uuid": str(created_request["uuid"]),
            "submit_http_ms": submit_http_ms,
            "first_seen_ms": first_seen_ms,
            "new_rule_count": len(new_rule_uuids),
            "new_rule_uuids": sorted(new_rule_uuids),
            "dht_rule_count_after_submit": len(latest_rules),
        }
        log(
            f"[{row['phase']}] run={row['run_index']:02d} "
            f"submit_http_ms={submit_http_ms:.3f} "
            f"first_seen_ms={first_seen_ms:.3f} "
            f"new_rule_count={len(new_rule_uuids)}"
        )

        if not args.keep_withdrawn_state:
            grant_consent(
                session,
                api_base,
                home_uuid=home_uuid,
                application_uuid=application_uuid,
                consent_uuid=consent_uuid,
            )
            wait_until_rules_removed(
                session,
                api_base,
                home_uuid=home_uuid,
                target_rule_uuids=new_rule_uuids,
                timeout_s=args.settle_timeout,
                poll_interval_s=args.poll_interval,
            )

        if row["phase"] == "measured":
            measured_rows.append(row)

    submit_http_values = [float(item["submit_http_ms"]) for item in measured_rows]
    first_seen_values = [float(item["first_seen_ms"]) for item in measured_rows]

    submit_stats = summarize_ms(submit_http_values)
    first_seen_stats = summarize_ms(first_seen_values)

    log()
    for line in stats_block_lines("Submit HTTP latency", submit_stats):
        log(line)
    log()
    for line in stats_block_lines("End-to-end first-seen latency", first_seen_stats):
        log(line)

    report = {
        "benchmark": "policy_propagation_latency",
        "base_url": args.base_url,
        "api_base": api_base,
        "ds_email": args.ds_email,
        "home_uuid": home_uuid,
        "application_id": args.application_id,
        "application_name": application_name,
        "application_title": application_title,
        "application_uuid": application_uuid,
        "consent_uuid": consent_uuid,
        "consent_content": consent_content,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "settle_timeout_s": args.settle_timeout,
        "poll_interval_s": args.poll_interval,
        "skip_refresh": args.skip_refresh,
        "keep_withdrawn_state": args.keep_withdrawn_state,
        "submit_http_stats": submit_stats,
        "first_seen_stats": first_seen_stats,
        "runs": measured_rows,
        "notes": [
            "submit_http_ms measures POST /api/requests/submit from client send to HTTP response completion.",
            "first_seen_ms measures from client send to first observation of new privacy_rule UUIDs through the DHT proxy endpoint.",
            f"Target selection uses application {args.application_id!r} and consent content {args.consent_content!r}.",
            "In testing mode the DHT is mocked/in-memory, so values are useful for harness validation but not representative of Smartotum network latency.",
        ],
    }

    if args.json_out:
        json_path = dump_json_report(report, args.json_out)
        log()
        log(f"JSON report written to {json_path}")
    if args.csv_out:
        csv_path = dump_csv_rows(
            [
                "run_index",
                "phase",
                "request_uuid",
                "submit_http_ms",
                "first_seen_ms",
                "new_rule_count",
                "new_rule_uuids",
                "dht_rule_count_after_submit",
            ],
            measured_rows,
            args.csv_out,
        )
        log(f"CSV report written to {csv_path}")
    if args.txt_out:
        txt_lines: list[str] = []
        append_section(
            txt_lines,
            "Policy Propagation Latency",
            [
                f"Base URL         : {args.base_url}",
                f"API Base         : {api_base}",
                f"Data Subject     : {args.ds_email}",
                f"Home UUID        : {home_uuid}",
                f"Application ID   : {args.application_id}",
                f"Application Name : {application_name}",
                f"Application Title: {application_title}",
                f"Application UUID : {application_uuid}",
                f"Consent UUID     : {consent_uuid}",
                f"Consent Content  : {consent_content}",
                f"Measured runs    : {args.iterations}",
                f"Warmup runs      : {args.warmup}",
                f"Settle timeout s : {args.settle_timeout}",
                f"Poll interval s  : {args.poll_interval}",
                f"Skip refresh     : {'yes' if args.skip_refresh else 'no'}",
                f"Keep withdrawn   : {'yes' if args.keep_withdrawn_state else 'no'}",
            ],
        )
        append_section(txt_lines, "Submit HTTP latency", stats_block_lines("", submit_stats)[1:])
        append_section(
            txt_lines,
            "End-to-end first-seen latency",
            stats_block_lines("", first_seen_stats)[1:],
        )
        append_section(
            txt_lines,
            "Notes",
            report["notes"],
        )
        txt_path = dump_text_report(txt_lines, args.txt_out)
        print(f"TXT report written to {txt_path}")


if __name__ == "__main__":
    main()
