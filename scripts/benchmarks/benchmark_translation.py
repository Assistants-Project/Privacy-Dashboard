from __future__ import annotations

import argparse
import time
from typing import Any, Callable

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
SIFIS_BASE_IRI = "http://elite.polito.it/ontologies/sifis-home.owl#"


def build_api_base(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/api"):
        return normalized
    return f"{normalized}/api"


def request_raw(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected_status: int | tuple[int, ...] = 200,
    **kwargs: Any,
) -> requests.Response:
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
    return response


def request_json(
    session: requests.Session,
    method: str,
    url: str,
    *,
    expected_status: int | tuple[int, ...] = 200,
    **kwargs: Any,
) -> Any:
    response = request_raw(
        session,
        method,
        url,
        expected_status=expected_status,
        **kwargs,
    )
    if not response.content:
        return None
    return response.json()


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


def discover_rule_primitives(session: requests.Session, api_base: str, home_uuid: str) -> dict[str, Any]:
    time_triggers = request_json(
        session,
        "GET",
        f"{api_base}/sifis/homes/{home_uuid}/trigger-services/sifis_time/triggers",
        expected_status=200,
    )
    trigger_by_id = {item["id"]: item for item in time_triggers}
    always_trigger = trigger_by_id.get("sifis_always_trigger")
    weekly_trigger = trigger_by_id.get("sifis_weekly_timer_trigger")
    if not always_trigger or not weekly_trigger:
        raise RuntimeError("Could not discover always/weekly timer triggers for service sifis_time")

    weekly_trigger_details = request_json(
        session,
        "GET",
        f"{api_base}/sifis/homes/{home_uuid}/trigger-services/sifis_time/triggers/{weekly_trigger['id']}/details",
        expected_status=200,
    )
    time_detail_urls: dict[str, str] = {}
    days_detail_url: str | None = None
    for detail in weekly_trigger_details:
        name = str(detail.get("name") or "").strip().lower()
        detail_url = str(detail["url"])
        if name == "from":
            time_detail_urls["from"] = detail_url
        elif name == "to":
            time_detail_urls["to"] = detail_url
        elif detail.get("type") == "days":
            days_detail_url = detail_url

    if "from" not in time_detail_urls or "to" not in time_detail_urls:
        raise RuntimeError("Could not discover From/To trigger detail URLs for weekly timer")

    video_actions = request_json(
        session,
        "GET",
        f"{api_base}/sifis/homes/{home_uuid}/action-services/sifis_video/actions",
        expected_status=200,
    )
    action = next(
        (item for item in video_actions if item.get("id") == "sifis_all_video_actions"),
        None,
    )
    if action is None and video_actions:
        action = video_actions[0]
    if action is None:
        raise RuntimeError("Could not discover a video action for service sifis_video")

    action_details = request_json(
        session,
        "GET",
        f"{api_base}/sifis/homes/{home_uuid}/action-services/sifis_video/actions/{action['id']}/details",
        expected_status=200,
    )
    location_detail = next(
        (item for item in action_details if item.get("type") == "location"),
        None,
    )
    if not location_detail:
        raise RuntimeError("Could not discover location detail for the selected video action")
    entire_home = next(
        (item for item in location_detail.get("alternatives", []) if item.get("name") == "Entire Home"),
        None,
    )
    if not entire_home:
        entire_home = {
            "name": "Entire Home",
            "url": f"http://elite.polito.it/ontologies/sifis-home.owl/{home_uuid}#location-home",
        }

    return {
        "always_trigger_url": str(always_trigger["url"]),
        "weekly_trigger_url": str(weekly_trigger["url"]),
        "time_detail_urls": time_detail_urls,
        "days_detail_url": days_detail_url,
        "action_url": str(action["url"]),
        "location_detail_url": str(location_detail["url"]),
        "entire_home": entire_home,
    }


def build_simple_rule(subject: str, primitives: dict[str, Any]) -> dict[str, Any]:
    return {
        "effect": "deny",
        "subject": subject,
        "expirationDate": "2099-12-31",
        "trigger": {
            "url": primitives["always_trigger_url"],
            "details": [],
        },
        "action": {
            "url": primitives["action_url"],
            "details": [
                {
                    "url": primitives["location_detail_url"],
                    "name": "Location",
                    "type": "location",
                    "value": primitives["entire_home"],
                }
            ],
        },
    }


def build_temporal_rule(subject: str, primitives: dict[str, Any]) -> dict[str, Any]:
    details = [
        {
            "url": primitives["time_detail_urls"]["from"],
            "name": "From",
            "type": "time",
            "value": "09",
        },
        {
            "url": primitives["time_detail_urls"]["to"],
            "name": "To",
            "type": "time",
            "value": "17",
        },
    ]
    if primitives["days_detail_url"]:
        details.append(
            {
                "url": primitives["days_detail_url"],
                "name": "Days of the Week",
                "type": "days",
                "value": ["Monday", "Wednesday", "Friday"],
            }
        )

    return {
        "effect": "deny",
        "subject": subject,
        "expirationDate": "2099-12-31",
        "trigger": {
            "url": primitives["weekly_trigger_url"],
            "details": details,
        },
        "action": {
            "url": primitives["action_url"],
            "details": [
                {
                    "url": primitives["location_detail_url"],
                    "name": "Location",
                    "type": "location",
                    "value": primitives["entire_home"],
                }
            ],
        },
    }


def create_rule(session: requests.Session, api_base: str, home_uuid: str, rule_payload: dict[str, Any]) -> int:
    response = request_json(
        session,
        "POST",
        f"{api_base}/sifis/homes/{home_uuid}/rules",
        expected_status=200,
        json=rule_payload,
    )
    return int(response["id"])


def delete_rule(session: requests.Session, api_base: str, home_uuid: str, rule_id: int) -> None:
    request_raw(
        session,
        "DELETE",
        f"{api_base}/sifis/homes/{home_uuid}/rules/{rule_id}",
        expected_status=200,
    )


def measure_download(
    session: requests.Session,
    api_base: str,
    home_uuid: str,
    rule_id: int,
) -> tuple[float, int, str]:
    t0 = time.perf_counter_ns()
    response = request_raw(
        session,
        "POST",
        f"{api_base}/sifis/homes/{home_uuid}/rules/{rule_id}/download",
        expected_status=200,
    )
    elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
    return elapsed_ms, len(response.content), response.headers.get("content-type", "")


def benchmark_single_rule(
    session: requests.Session,
    api_base: str,
    home_uuid: str,
    *,
    log: Callable[[str], None],
    scenario_name: str,
    rule_payload: dict[str, Any],
    warmup: int,
    iterations: int,
) -> dict[str, Any]:
    rule_id = create_rule(session, api_base, home_uuid, rule_payload)
    try:
        total_runs = warmup + iterations
        measured_rows: list[dict[str, Any]] = []
        payload_sizes: list[int] = []
        content_types: set[str] = set()

        for index in range(total_runs):
            elapsed_ms, payload_size, content_type = measure_download(
                session, api_base, home_uuid, rule_id
            )
            content_types.add(content_type)
            payload_sizes.append(payload_size)
            phase = "warmup" if index < warmup else "measured"
            log(
                f"[{phase}] {scenario_name} run={index + 1:02d} "
                f"download_ms={elapsed_ms:.3f} payload_bytes={payload_size}"
            )
            if phase == "measured":
                measured_rows.append(
                    {
                        "run_index": index + 1,
                        "download_ms": elapsed_ms,
                        "payload_bytes": payload_size,
                        "content_type": content_type,
                    }
                )

        values = [float(item["download_ms"]) for item in measured_rows]
        stats = summarize_ms(values)
        log("")
        for line in stats_block_lines(f"{scenario_name} download latency", stats):
            log(line)
        log("")
        return {
            "scenario": scenario_name,
            "rule_id": rule_id,
            "stats": stats,
            "runs": measured_rows,
            "payload_bytes_min": min(payload_sizes),
            "payload_bytes_max": max(payload_sizes),
            "content_types": sorted(content_types),
        }
    finally:
        delete_rule(session, api_base, home_uuid, rule_id)


def benchmark_multi_subject_surrogate(
    session: requests.Session,
    api_base: str,
    home_uuid: str,
    *,
    log: Callable[[str], None],
    primitives: dict[str, Any],
    subject_count: int,
    warmup: int,
    iterations: int,
) -> dict[str, Any]:
    rule_ids: list[int] = []
    try:
        for index in range(subject_count):
            subject = f"subject{index + 1}@example.com"
            rule_ids.append(
                create_rule(
                    session,
                    api_base,
                    home_uuid,
                    build_simple_rule(subject, primitives),
                )
            )

        total_runs = warmup + iterations
        batch_rows: list[dict[str, Any]] = []
        per_rule_values: list[float] = []

        for run_index in range(total_runs):
            t0 = time.perf_counter_ns()
            single_run_values: list[float] = []
            for rule_id in rule_ids:
                elapsed_ms, _payload_size, _content_type = measure_download(
                    session, api_base, home_uuid, rule_id
                )
                single_run_values.append(elapsed_ms)
            batch_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
            phase = "warmup" if run_index < warmup else "measured"
            log(
                f"[{phase}] multi_subject_surrogate run={run_index + 1:02d} "
                f"batch_ms={batch_ms:.3f} per_rule_mean_ms={sum(single_run_values) / len(single_run_values):.3f}"
            )
            if phase == "measured":
                batch_rows.append(
                    {
                        "run_index": run_index + 1,
                        "batch_ms": batch_ms,
                        "per_rule_mean_ms": sum(single_run_values) / len(single_run_values),
                        "subjects": subject_count,
                    }
                )
                per_rule_values.extend(single_run_values)

        batch_stats = summarize_ms([float(item["batch_ms"]) for item in batch_rows])
        per_rule_stats = summarize_ms(per_rule_values)
        log("")
        for line in stats_block_lines("multi_subject_surrogate batch latency", batch_stats):
            log(line)
        log("")
        for line in stats_block_lines("multi_subject_surrogate per-download latency", per_rule_stats):
            log(line)
        log("")
        return {
            "scenario": "multi_subject_surrogate",
            "subject_count": subject_count,
            "rule_ids": rule_ids,
            "batch_stats": batch_stats,
            "per_rule_stats": per_rule_stats,
            "runs": batch_rows,
            "notes": [
                "The current rule model accepts a single string subject, not a true subject list.",
                "This scenario emulates a multi-subject policy by translating the same logical rule for multiple distinct subjects and measuring both batch and per-rule timings.",
            ],
        }
    finally:
        for rule_id in rule_ids:
            delete_rule(session, api_base, home_uuid, rule_id)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark XACML translation latency through the Flask download endpoint "
            "for representative SIFIS rules."
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
    parser.add_argument("--home-uuid")
    parser.add_argument("--iterations", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--multi-subject-count", type=int, default=3)
    parser.add_argument("--skip-refresh", action="store_true")
    parser.add_argument("--json-out")
    parser.add_argument("--csv-out")
    parser.add_argument("--txt-out")
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")
    if args.warmup < 0:
        raise SystemExit("--warmup must be >= 0")
    if args.multi_subject_count < 2:
        raise SystemExit("--multi-subject-count must be >= 2")

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
            raise SystemExit(ds_password_fallback_error("benchmark_translation.py")) from exc
        raise
    if used_testing_fallback:
        log("No --ds-password provided; using the testing-only Data Subject password fallback.")
    if not args.skip_refresh:
        refresh_testing_snapshot(session, api_base)

    home_uuid = get_home_uuid(session, api_base, args.home_uuid)
    primitives = discover_rule_primitives(session, api_base, home_uuid)

    simple_result = benchmark_single_rule(
        session,
        api_base,
        home_uuid,
        log=log,
        scenario_name="simple_deny",
        rule_payload=build_simple_rule(args.ds_email, primitives),
        warmup=args.warmup,
        iterations=args.iterations,
    )
    temporal_result = benchmark_single_rule(
        session,
        api_base,
        home_uuid,
        log=log,
        scenario_name="temporal_deny",
        rule_payload=build_temporal_rule(args.ds_email, primitives),
        warmup=args.warmup,
        iterations=args.iterations,
    )
    multi_subject_result = benchmark_multi_subject_surrogate(
        session,
        api_base,
        home_uuid,
        log=log,
        primitives=primitives,
        subject_count=args.multi_subject_count,
        warmup=args.warmup,
        iterations=args.iterations,
    )

    report = {
        "benchmark": "ptp_translation_time",
        "base_url": args.base_url,
        "api_base": api_base,
        "ds_email": args.ds_email,
        "home_uuid": home_uuid,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "multi_subject_count": args.multi_subject_count,
        "skip_refresh": args.skip_refresh,
        "scenarios": [
            simple_result,
            temporal_result,
            multi_subject_result,
        ],
        "notes": [
            "The metric is measured at the Flask endpoint /api/sifis/homes/<home_uuid>/rules/<rule_id>/download.",
            "Rule creation and deletion are excluded from the timed section.",
        ],
    }

    if args.json_out:
        json_path = dump_json_report(report, args.json_out)
        log(f"JSON report written to {json_path}")
    if args.csv_out:
        csv_rows: list[dict[str, Any]] = []
        for scenario in report["scenarios"]:
            scenario_name = str(scenario["scenario"])
            if scenario_name == "multi_subject_surrogate":
                for run in scenario["runs"]:
                    csv_rows.append(
                        {
                            "scenario": scenario_name,
                            "run_index": run["run_index"],
                            "download_ms": "",
                            "payload_bytes": "",
                            "content_type": "",
                            "batch_ms": run["batch_ms"],
                            "per_rule_mean_ms": run["per_rule_mean_ms"],
                            "subjects": run["subjects"],
                        }
                    )
            else:
                for run in scenario["runs"]:
                    csv_rows.append(
                        {
                            "scenario": scenario_name,
                            "run_index": run["run_index"],
                            "download_ms": run["download_ms"],
                            "payload_bytes": run["payload_bytes"],
                            "content_type": run["content_type"],
                            "batch_ms": "",
                            "per_rule_mean_ms": "",
                            "subjects": "",
                        }
                    )
        csv_path = dump_csv_rows(
            [
                "scenario",
                "run_index",
                "download_ms",
                "payload_bytes",
                "content_type",
                "batch_ms",
                "per_rule_mean_ms",
                "subjects",
            ],
            csv_rows,
            args.csv_out,
        )
        log(f"CSV report written to {csv_path}")
    if args.txt_out:
        txt_lines: list[str] = []
        append_section(
            txt_lines,
            "PTP Translation Time",
            [
                f"Base URL           : {args.base_url}",
                f"API Base           : {api_base}",
                f"Data Subject       : {args.ds_email}",
                f"Home UUID          : {home_uuid}",
                f"Measured runs      : {args.iterations}",
                f"Warmup runs        : {args.warmup}",
                f"Multi-subject size : {args.multi_subject_count}",
                f"Skip refresh       : {'yes' if args.skip_refresh else 'no'}",
                "Timed endpoint     : POST /api/sifis/homes/<home_uuid>/rules/<rule_id>/download",
            ],
        )
        for scenario in report["scenarios"]:
            scenario_name = str(scenario["scenario"])
            if scenario_name == "multi_subject_surrogate":
                body = [
                    f"Subject count : {scenario['subject_count']}",
                    "Batch latency",
                    *stats_block_lines("", scenario["batch_stats"])[1:],
                    "",
                    "Per-download latency",
                    *stats_block_lines("", scenario["per_rule_stats"])[1:],
                    "",
                    *scenario.get("notes", []),
                ]
            else:
                body = [
                    *stats_block_lines("", scenario["stats"])[1:],
                    f"payload_bytes_min : {scenario['payload_bytes_min']}",
                    f"payload_bytes_max : {scenario['payload_bytes_max']}",
                    f"content_types     : {', '.join(scenario['content_types'])}",
                ]
            append_section(txt_lines, scenario_name, body)
        append_section(txt_lines, "Notes", report["notes"])
        txt_path = dump_text_report(txt_lines, args.txt_out)
        print(f"TXT report written to {txt_path}")


if __name__ == "__main__":
    main()
