from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

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


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_COLLECTION = PROJECT_ROOT / "backend" / "testing" / "tests" / "Privacy-Dashboard-API.postman_collection_cleaned.json"
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def declared_route_count() -> int:
    controllers_dir = PROJECT_ROOT / "backend" / "app" / "controllers"
    count = 0
    for path in controllers_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        count += len(re.findall(r"@[\w_]+\.(?:route)\(", text))
    return count


def normalize_path(path: str) -> str:
    normalized_segments = []
    for segment in path.split("/"):
        if not segment:
            continue
        if UUID_RE.match(segment):
            normalized_segments.append("<uuid>")
        elif segment.isdigit():
            normalized_segments.append("<id>")
        elif "@" in segment:
            normalized_segments.append("<email>")
        else:
            normalized_segments.append(segment)
    return "/" + "/".join(normalized_segments)


def extract_method(execution: dict[str, Any]) -> str:
    return str(execution.get("request", {}).get("method", "GET")).upper()


def extract_path(execution: dict[str, Any]) -> str:
    request_url = execution.get("request", {}).get("url", {})
    if isinstance(request_url, dict):
        path = request_url.get("path")
        if isinstance(path, list) and path:
            return "/" + "/".join(str(segment) for segment in path)
        raw = request_url.get("raw")
        if raw:
            return urlparse(str(raw)).path
    elif request_url:
        return urlparse(str(request_url)).path
    return "/"


def load_newman_executions(report_path: Path) -> list[dict[str, Any]]:
    payload = load_newman_report(report_path)
    return list(payload.get("run", {}).get("executions", []))


def load_newman_report(report_path: Path) -> dict[str, Any]:
    return json.loads(report_path.read_text(encoding="utf-8"))


def summarize_newman_failures(
    report_payload: dict[str, Any], *, limit: int = 5
) -> tuple[int, list[str]]:
    failures = list(report_payload.get("run", {}).get("failures", []))
    lines: list[str] = []
    for failure in failures[:limit]:
        source_name = str(failure.get("source", {}).get("name", "<unknown request>"))
        error = failure.get("error", {})
        test_name = str(error.get("test") or failure.get("at") or "<unknown assertion>")
        message = str(error.get("message") or error.get("name") or "Unknown Newman failure")
        lines.append(f"{source_name} :: {test_name} :: {message}")
    remaining = len(failures) - len(lines)
    if remaining > 0:
        lines.append(f"... {remaining} additional Newman failures not shown")
    return len(failures), lines


def require_docker() -> None:
    try:
        subprocess.run(
            ["docker", "version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        raise RuntimeError(
            "Docker is required for this benchmark because Newman is executed through the postman/newman image."
        ) from exc


def run_newman_iteration(
    *,
    collection_path: Path,
    base_url: str,
    output_path: Path,
    dc_email: str,
    dc_password: str,
    ds_email: str,
    ds_password: str,
    delegate_email: str,
    dpo_email: str,
    dpo_password: str,
    marketplace_integration_token: str,
    dc_updated_password: str,
    dpo_updated_email: str,
    dpo_updated_password: str,
) -> subprocess.CompletedProcess[str]:
    output_dir = output_path.parent
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{collection_path}:/etc/newman/collection.json:ro",
        "-v",
        f"{output_dir}:/tmp/newman",
        "postman/newman:alpine",
        "run",
        "/etc/newman/collection.json",
        "--reporters",
        "json",
        "--reporter-json-export",
        f"/tmp/newman/{output_path.name}",
        "--env-var",
        f"baseURL={base_url}",
        "--env-var",
        f"dc_email={dc_email}",
        "--env-var",
        f"dc_password={dc_password}",
        "--env-var",
        f"ds_email={ds_email}",
        "--env-var",
        f"ds_password={ds_password}",
        "--env-var",
        f"delegate_email={delegate_email}",
        "--env-var",
        f"dpo_email={dpo_email}",
        "--env-var",
        f"dpo_password={dpo_password}",
        "--env-var",
        f"marketplace_integration_token={marketplace_integration_token}",
        "--env-var",
        f"dc_updated_password={dc_updated_password}",
        "--env-var",
        f"dpo_updated_email={dpo_updated_email}",
        "--env-var",
        f"dpo_updated_password={dpo_updated_password}",
    ]
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the existing Postman/Newman API collection and summarize response times "
            "grouped by normalized HTTP endpoint."
        )
    )
    parser.add_argument(
        "--base-url",
        default="http://host.docker.internal:5050",
        help=(
            "Base URL visible from inside the Dockerized Newman container. "
            "For a backend running on the host, host.docker.internal is usually correct on macOS/Windows."
        ),
    )
    parser.add_argument("--collection", default=str(DEFAULT_COLLECTION))
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--success-only", action="store_true")
    parser.add_argument("--json-out")
    parser.add_argument("--csv-out")
    parser.add_argument("--txt-out")
    parser.add_argument("--dc-email", default="controller.smartotum@example.com")
    parser.add_argument("--dc-password", default="controllersmartotum")
    parser.add_argument("--ds-email", default="s312192@studenti.polito.it")
    parser.add_argument(
        "--ds-password",
        help=(
            "Real Smartotum password for the Data Subject. If omitted, Newman uses "
            "the testing-only fallback password, which works only with FLASK_ENV=testing."
        ),
    )
    parser.add_argument("--delegate-email", default="controller.general@example.com")
    parser.add_argument("--dpo-email", default="dpo.general@example.com")
    parser.add_argument("--dpo-password", default="dpogeneral")
    parser.add_argument(
        "--marketplace-integration-token",
        default="BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4",
    )
    parser.add_argument("--dc-updated-password", default="controllersmartotum-updated")
    parser.add_argument("--dpo-updated-email", default="dpo.general.updated@example.com")
    parser.add_argument("--dpo-updated-password", default="dpogeneral-updated")
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")

    terminal_lines: list[str] = []

    def log(message: str = "") -> None:
        print(message)
        terminal_lines.append(message)

    require_docker()

    collection_path = Path(args.collection).expanduser().resolve()
    if not collection_path.exists():
        raise SystemExit(f"Collection file not found: {collection_path}")

    ds_password, used_testing_fallback = resolve_ds_password(args.ds_password)
    if used_testing_fallback:
        log("No --ds-password provided; using the testing-only Data Subject password fallback.")

    endpoint_groups: dict[str, dict[str, Any]] = {}
    newman_exit_codes: list[int] = []
    newman_failure_count = 0
    newman_failure_lines: list[str] = []

    with tempfile.TemporaryDirectory(prefix="privacy-dashboard-newman-") as tmpdir:
        temp_dir = Path(tmpdir)

        for iteration in range(1, args.iterations + 1):
            report_path = temp_dir / f"newman-report-{iteration}.json"
            log(f"Running Newman iteration {iteration}/{args.iterations}")
            result = run_newman_iteration(
                collection_path=collection_path,
                base_url=args.base_url,
                output_path=report_path,
                dc_email=args.dc_email,
                dc_password=args.dc_password,
                ds_email=args.ds_email,
                ds_password=ds_password,
                delegate_email=args.delegate_email,
                dpo_email=args.dpo_email,
                dpo_password=args.dpo_password,
                marketplace_integration_token=args.marketplace_integration_token,
                dc_updated_password=args.dc_updated_password,
                dpo_updated_email=args.dpo_updated_email,
                dpo_updated_password=args.dpo_updated_password,
            )
            newman_exit_codes.append(result.returncode)
            if not report_path.exists():
                if used_testing_fallback:
                    raise SystemExit(
                        f"{ds_password_fallback_error('benchmark_api_collection.py')} "
                        "Newman did not produce a JSON report; if the backend is not in "
                        "FLASK_ENV=testing, rerun with --ds-password <real Smartotum password>."
                    )
                stderr_tail = result.stderr.strip().splitlines()[-10:]
                stdout_tail = result.stdout.strip().splitlines()[-10:]
                details = "\n".join(line for line in stdout_tail + stderr_tail if line)
                raise SystemExit(
                    "Newman failed before producing a JSON report.\n"
                    f"Exit status: {result.returncode}\n"
                    f"{details or 'No stdout/stderr captured from Newman.'}"
                )

            report_payload = load_newman_report(report_path)
            if result.returncode != 0:
                failure_count, failure_lines = summarize_newman_failures(report_payload)
                newman_failure_count += failure_count
                if failure_lines:
                    log(
                        f"Newman iteration {iteration} exited with status {result.returncode}; "
                        f"continuing with the recorded executions ({failure_count} failure(s) in the collection)."
                    )
                    for failure_line in failure_lines:
                        if failure_line not in newman_failure_lines:
                            newman_failure_lines.append(failure_line)

            executions = list(report_payload.get("run", {}).get("executions", []))
            for execution in executions:
                response = execution.get("response")
                if not response:
                    continue
                status_code = int(response.get("code", 0))
                if args.success_only and not (200 <= status_code < 400):
                    continue

                path = extract_path(execution)
                method = extract_method(execution)
                normalized = normalize_path(path)
                key = f"{method} {normalized}"
                group = endpoint_groups.setdefault(
                    key,
                    {
                        "method": method,
                        "normalized_path": normalized,
                        "raw_paths": set(),
                        "request_names": set(),
                        "status_codes": set(),
                        "response_times_ms": [],
                    },
                )
                group["raw_paths"].add(path)
                group["request_names"].add(str(execution.get("item", {}).get("name", "")))
                group["status_codes"].add(status_code)
                group["response_times_ms"].append(float(response.get("responseTime", 0.0)))

    rows = []
    for key, group in sorted(endpoint_groups.items()):
        stats = summarize_ms(group["response_times_ms"])
        rows.append(
            {
                "endpoint": key,
                "samples": stats["count"],
                "mean_ms": stats["mean_ms"],
                "median_ms": stats["median_ms"],
                "p95_ms": stats["p95_ms"],
                "min_ms": stats["min_ms"],
                "max_ms": stats["max_ms"],
                "status_codes": ",".join(str(code) for code in sorted(group["status_codes"])),
            }
        )

    if not rows:
        raise SystemExit(
            "No executions were aggregated. If you used --success-only, try without it to inspect the raw collection behavior."
        )

    overall_values = [float(value) for group in endpoint_groups.values() for value in group["response_times_ms"]]
    overall_stats = summarize_ms(overall_values)
    log()
    for line in stats_block_lines("Aggregated execution latency", overall_stats):
        log(line)
    log()
    log(f"Declared controller routes : {declared_route_count()}")
    log(f"Observed endpoint groups   : {len(rows)}")
    if any(code != 0 for code in newman_exit_codes):
        log(f"Newman exit codes         : {', '.join(str(code) for code in newman_exit_codes)}")
        log(f"Collection failures       : {newman_failure_count}")
        if newman_failure_lines:
            log("Sample Newman failures:")
            for failure_line in newman_failure_lines[:5]:
                log(f"  - {failure_line}")

    report = {
        "benchmark": "api_response_times_collection",
        "base_url": args.base_url,
        "collection_path": str(collection_path),
        "iterations": args.iterations,
        "success_only": args.success_only,
        "dc_email": args.dc_email,
        "ds_email": args.ds_email,
        "delegate_email": args.delegate_email,
        "dpo_email": args.dpo_email,
        "newman_exit_codes": newman_exit_codes,
        "collection_failure_count": newman_failure_count,
        "collection_failure_samples": newman_failure_lines[:10],
        "declared_controller_routes": declared_route_count(),
        "observed_endpoint_groups": len(rows),
        "overall_stats": overall_stats,
        "endpoints": [
            {
                **row,
                "raw_paths": sorted(endpoint_groups[row["endpoint"]]["raw_paths"]),
                "request_names": sorted(endpoint_groups[row["endpoint"]]["request_names"]),
            }
            for row in rows
        ],
        "notes": [
            "This benchmark reuses the maintained Postman collection instead of reimplementing 74 HTTP calls by hand.",
            "Use --success-only to approximate nominal-path latency and omit 401/403/422 regression checks from the summary.",
            "Paths are normalized by replacing UUID-like segments, numeric ids, and emails to reduce fragmentation across iterations.",
            "If Newman exits non-zero because collection assertions fail, the benchmark still aggregates the executions present in the JSON report.",
        ],
    }

    if args.json_out:
        json_path = dump_json_report(report, args.json_out)
        log(f"JSON report written to {json_path}")
    if args.csv_out:
        csv_path = dump_csv_rows(
            [
                "endpoint",
                "samples",
                "mean_ms",
                "median_ms",
                "p95_ms",
                "min_ms",
                "max_ms",
                "status_codes",
            ],
            rows,
            args.csv_out,
        )
        log(f"CSV report written to {csv_path}")
    if args.txt_out:
        txt_lines: list[str] = []
        append_section(
            txt_lines,
            "API Collection Response Times",
            [
                f"Base URL                 : {args.base_url}",
                f"Collection               : {collection_path}",
                f"Measured Newman runs     : {args.iterations}",
                f"Success-only aggregation : {'yes' if args.success_only else 'no'}",
                f"Data Subject             : {args.ds_email}",
                f"Data Controller          : {args.dc_email}",
                f"Delegate                 : {args.delegate_email}",
                f"DPO                      : {args.dpo_email}",
                f"Declared controller routes: {declared_route_count()}",
                f"Observed endpoint groups : {len(rows)}",
            ],
        )
        append_section(
            txt_lines,
            "Aggregated execution latency",
            stats_block_lines("", overall_stats)[1:],
        )
        if any(code != 0 for code in newman_exit_codes):
            append_section(
                txt_lines,
                "Collection failures",
                [
                    f"Newman exit codes   : {', '.join(str(code) for code in newman_exit_codes)}",
                    f"Failure count       : {newman_failure_count}",
                    *[f"- {line}" for line in newman_failure_lines[:5]],
                ],
            )
        top_by_mean = sorted(rows, key=lambda row: float(row["mean_ms"]), reverse=True)[:10]
        append_section(
            txt_lines,
            "Slowest endpoints by mean latency",
            [
                f"{row['endpoint']} | mean {row['mean_ms']:.3f} ms | median {row['median_ms']:.3f} ms | p95 {row['p95_ms']:.3f} ms | samples {row['samples']}"
                for row in top_by_mean
            ],
        )
        append_section(txt_lines, "Notes", report["notes"])
        txt_path = dump_text_report(txt_lines, args.txt_out)
        print(f"TXT report written to {txt_path}")


if __name__ == "__main__":
    main()
