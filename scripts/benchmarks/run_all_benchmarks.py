from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from common import append_section, dump_text_report


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_DIR = Path(__file__).resolve().parent
DEFAULT_RESULTS_ROOT = BENCHMARKS_DIR / "results"
DEFAULT_API_COLLECTION = PROJECT_ROOT / "backend" / "testing" / "tests" / "Privacy-Dashboard-API.postman_collection_cleaned.json"
DEFAULT_OWL_ONTOLOGY_DIRECTORY = str(PROJECT_ROOT / "backend" / "app" / "ontologies")
DEFAULT_PYTHON = (
    PROJECT_ROOT / ".venv" / "bin" / "python"
    if (PROJECT_ROOT / ".venv" / "bin" / "python").exists()
    else Path(sys.executable)
)

BENCHMARK_ORDER = ["api", "withdraw", "translation", "petrinet", "owl"]


def build_output_dir(requested_output_dir: str | None) -> Path:
    if requested_output_dir:
        output_dir = Path(requested_output_dir).expanduser().resolve()
    else:
        output_dir = DEFAULT_RESULTS_ROOT.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def add_value_arg(cmd: list[str], flag: str, value: str | None) -> None:
    if value is None:
        return
    cmd.extend([flag, value])


def format_stats_short(stats: dict[str, Any]) -> str:
    return (
        f"mean {float(stats['mean_ms']):.3f} ms, "
        f"median {float(stats['median_ms']):.3f} ms, "
        f"p95 {float(stats['p95_ms']):.3f} ms, "
        f"min {float(stats['min_ms']):.3f} ms, "
        f"max {float(stats['max_ms']):.3f} ms"
    )


def format_enabled(value: bool) -> str:
    return "yes" if value else "no"


def run_benchmark(name: str, cmd: list[str]) -> dict[str, Any]:
    started_at = time.perf_counter()
    completed = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    elapsed_s = time.perf_counter() - started_at
    return {
        "name": name,
        "command": cmd,
        "returncode": completed.returncode,
        "elapsed_s": elapsed_s,
        "status": "ok" if completed.returncode == 0 else "failed",
    }


def load_report_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def summarize_withdraw(report: dict[str, Any]) -> list[str]:
    return [
        "mode             : HTTP withdraw request + DHT visibility polling",
        f"base_url         : {report['base_url']}",
        f"ds_email         : {report.get('ds_email', '<unknown>')}",
        f"home_uuid        : {report['home_uuid']}",
        f"application_id   : {report.get('application_id', report['application_name'])}",
        f"application_name : {report['application_name']}",
        f"consent_content  : {report['consent_content']}",
        f"iterations       : {report['iterations']}",
        f"warmup           : {report['warmup']}",
        f"settle_timeout_s : {report['settle_timeout_s']}",
        f"poll_interval_s  : {report['poll_interval_s']}",
        f"skip_refresh     : {format_enabled(bool(report.get('skip_refresh')))}",
        f"keep_withdrawn   : {format_enabled(bool(report.get('keep_withdrawn_state')))}",
        f"submit_http      : {format_stats_short(report['submit_http_stats'])}",
        f"first_seen       : {format_stats_short(report['first_seen_stats'])}",
    ]


def summarize_translation(report: dict[str, Any]) -> list[str]:
    lines: list[str] = [
        "mode                 : Flask endpoint end-to-end",
        "timed_endpoint       : POST /api/sifis/homes/<home_uuid>/rules/<rule_id>/download",
        f"base_url             : {report['base_url']}",
        f"ds_email             : {report.get('ds_email', '<unknown>')}",
        f"home_uuid            : {report['home_uuid']}",
        f"iterations           : {report['iterations']}",
        f"warmup               : {report['warmup']}",
        f"multi_subject_count  : {report['multi_subject_count']}",
        f"skip_refresh         : {format_enabled(bool(report.get('skip_refresh')))}",
    ]
    for scenario in report.get("scenarios", []):
        scenario_name = str(scenario["scenario"])
        if scenario_name == "multi_subject_surrogate":
            lines.append(
                f"{scenario_name} batch      : {format_stats_short(scenario['batch_stats'])}"
            )
            lines.append(
                f"{scenario_name} per-rule   : {format_stats_short(scenario['per_rule_stats'])}"
            )
        else:
            lines.append(
                f"{scenario_name:<24}: {format_stats_short(scenario['stats'])}"
            )
    return lines


def summarize_petrinet(report: dict[str, Any]) -> list[str]:
    lines = [
        "mode           : direct Python service call",
        f"rule_counts    : {', '.join(str(count) for count in report.get('rule_counts', []))}",
        f"iterations     : {report['iterations']}",
        f"warmup         : {report['warmup']}",
        f"conflict_type  : {report['conflict_type']}",
        "curve          :",
    ]
    lines.extend(
        (
            f"  rules={bucket['rule_count']} -> "
            f"{format_stats_short(bucket['stats'])}"
        )
        for bucket in report.get("curve", [])
    )
    return lines


def summarize_api(report: dict[str, Any]) -> list[str]:
    lines = [
        "mode              : Dockerized Newman collection replay",
        f"base_url          : {report['base_url']}",
        f"collection        : {report['collection_path']}",
        f"iterations        : {report['iterations']}",
        f"success_only      : {format_enabled(bool(report['success_only']))}",
        f"ds_email          : {report.get('ds_email', '<unknown>')}",
        f"dc_email          : {report.get('dc_email', '<unknown>')}",
        f"overall latency   : {format_stats_short(report['overall_stats'])}",
        f"endpoint groups   : {report['observed_endpoint_groups']}",
        f"controller routes : {report['declared_controller_routes']}",
        f"collection failures: {report.get('collection_failure_count', 0)}",
    ]
    for sample in report.get("collection_failure_samples", [])[:3]:
        lines.append(f"- {sample}")
    return lines


def summarize_owl(report: dict[str, Any]) -> list[str]:
    return [
        "mode              : direct Python OWLService initialization",
        f"ontology dir      : {report['ontology_directory']}",
        f"ontology file     : {report['ontology_file']}",
        f"iterations        : {report['iterations']}",
        f"warmup            : {report['warmup']}",
        f"suppress output   : {format_enabled(bool(report['suppress_reasoner_output']))}",
        f"owl init latency  : {format_stats_short(report['stats'])}",
    ]


def build_summary_lines(
    *,
    output_dir: Path,
    selected_benchmarks: list[str],
    benchmark_runs: list[dict[str, Any]],
    reports: dict[str, dict[str, Any] | None],
    artifact_paths: dict[str, dict[str, Path]],
) -> list[str]:
    lines: list[str] = []
    append_section(
        lines,
        "All Benchmarks Summary",
        [
            f"Output directory      : {output_dir}",
            f"Selected benchmarks   : {', '.join(selected_benchmarks)}",
            f"Completed benchmarks  : {sum(run['status'] == 'ok' for run in benchmark_runs)}",
            f"Failed benchmarks     : {sum(run['status'] != 'ok' for run in benchmark_runs)}",
            f"Python interpreter    : {DEFAULT_PYTHON}",
        ],
    )

    for run in benchmark_runs:
        name = str(run["name"])
        report = reports.get(name)
        paths = artifact_paths[name]
        body = [
            f"status      : {run['status']}",
            f"elapsed_s   : {run['elapsed_s']:.3f}",
            f"json        : {paths['json']}",
            f"csv         : {paths['csv']}",
            f"txt         : {paths['txt']}",
        ]
        if report is None:
            body.append("report      : missing JSON report")
        elif name == "withdraw":
            body.extend(summarize_withdraw(report))
        elif name == "translation":
            body.extend(summarize_translation(report))
        elif name == "petrinet":
            body.extend(summarize_petrinet(report))
        elif name == "api":
            body.extend(summarize_api(report))
        elif name == "owl":
            body.extend(summarize_owl(report))
        append_section(lines, name, body)
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run all benchmark scripts in sequence, save individual JSON/CSV/TXT artifacts, "
            "and produce a single summary.txt report."
        )
    )
    parser.add_argument(
        "--benchmarks",
        nargs="+",
        choices=BENCHMARK_ORDER,
        default=BENCHMARK_ORDER,
        help="Subset of benchmarks to run. Default: all.",
    )
    parser.add_argument(
        "--output-dir",
        help=(
            "Directory where all per-benchmark artifacts and summary.txt are written. "
            "If omitted, files are written directly under scripts/benchmarks/results."
        ),
    )
    parser.add_argument("--base-url", default="http://127.0.0.1:5050")
    parser.add_argument("--api-collection-base-url", default="http://host.docker.internal:5050")
    parser.add_argument("--ds-email", default="s312192@studenti.polito.it")
    parser.add_argument("--ds-password")
    parser.add_argument("--home-uuid")
    parser.add_argument("--skip-refresh", action="store_true")
    parser.add_argument("--withdraw-application-id", default="com.smartotum.smartotum-camera-manager")
    parser.add_argument("--withdraw-consent-content", default="Consent to Record Video Footage from Smart Home Cameras")
    parser.add_argument("--withdraw-iterations", type=int, default=10)
    parser.add_argument("--withdraw-warmup", type=int, default=2)
    parser.add_argument("--withdraw-settle-timeout", type=float, default=10.0)
    parser.add_argument("--withdraw-poll-interval", type=float, default=0.2)
    parser.add_argument("--withdraw-keep-withdrawn-state", action="store_true")
    parser.add_argument("--translation-iterations", type=int, default=30)
    parser.add_argument("--translation-warmup", type=int, default=5)
    parser.add_argument("--translation-multi-subject-count", type=int, default=3)
    parser.add_argument("--petrinet-rule-counts", nargs="+", type=int, default=[10, 25, 50])
    parser.add_argument("--petrinet-iterations", type=int, default=50)
    parser.add_argument("--petrinet-warmup", type=int, default=10)
    parser.add_argument("--petrinet-conflict-type", choices=("inconsistency", "redundancy"), default="inconsistency")
    parser.add_argument("--owl-ontology-directory", default=DEFAULT_OWL_ONTOLOGY_DIRECTORY)
    parser.add_argument("--owl-ontology-file", default="sifis-home.owl")
    parser.add_argument("--owl-iterations", type=int, default=10)
    parser.add_argument("--owl-warmup", type=int, default=2)
    parser.add_argument(
        "--owl-suppress-reasoner-output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When enabled, pass --suppress-reasoner-output to the OWL loading benchmark. Default: enabled.",
    )
    parser.add_argument("--api-collection", default=str(DEFAULT_API_COLLECTION))
    parser.add_argument("--api-iterations", type=int, default=1)
    parser.add_argument(
        "--api-success-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When enabled, pass --success-only to the API collection benchmark. Default: enabled.",
    )
    parser.add_argument("--dc-email", default="controller.smartotum@example.com")
    parser.add_argument("--dc-password", default="controllersmartotum")
    parser.add_argument("--delegate-email", default="controller.general@example.com")
    parser.add_argument("--dpo-email", default="dpo.general@example.com")
    parser.add_argument("--dpo-password", default="dpogeneral")
    parser.add_argument("--marketplace-integration-token", default="BS4bieIhYQxIREcnBleLx/qqlBvSnPJ4")
    parser.add_argument("--dc-updated-password", default="controllersmartotum-updated")
    parser.add_argument("--dpo-updated-email", default="dpo.general.updated@example.com")
    parser.add_argument("--dpo-updated-password", default="dpogeneral-updated")
    args = parser.parse_args()

    output_dir = build_output_dir(args.output_dir)
    selected_benchmarks = [
        benchmark_name
        for benchmark_name in BENCHMARK_ORDER
        if benchmark_name in set(args.benchmarks)
    ]
    benchmark_runs: list[dict[str, Any]] = []
    reports: dict[str, dict[str, Any] | None] = {}
    artifact_paths: dict[str, dict[str, Path]] = {}

    for benchmark_name in selected_benchmarks:
        if benchmark_name == "withdraw":
            json_path = output_dir / "withdraw-latency.json"
            csv_path = output_dir / "withdraw-latency.csv"
            txt_path = output_dir / "withdraw-latency.txt"
            cmd = [
                str(DEFAULT_PYTHON),
                str(BENCHMARKS_DIR / "benchmark_withdraw_latency.py"),
                "--base-url",
                args.base_url,
                "--ds-email",
                args.ds_email,
                "--application-id",
                args.withdraw_application_id,
                "--consent-content",
                args.withdraw_consent_content,
                "--iterations",
                str(args.withdraw_iterations),
                "--warmup",
                str(args.withdraw_warmup),
                "--settle-timeout",
                str(args.withdraw_settle_timeout),
                "--poll-interval",
                str(args.withdraw_poll_interval),
                "--json-out",
                str(json_path),
                "--csv-out",
                str(csv_path),
                "--txt-out",
                str(txt_path),
            ]
            add_value_arg(cmd, "--ds-password", args.ds_password)
            add_value_arg(cmd, "--home-uuid", args.home_uuid)
            if args.skip_refresh:
                cmd.append("--skip-refresh")
            if args.withdraw_keep_withdrawn_state:
                cmd.append("--keep-withdrawn-state")
        elif benchmark_name == "translation":
            json_path = output_dir / "translation-benchmark.json"
            csv_path = output_dir / "translation-benchmark.csv"
            txt_path = output_dir / "translation-benchmark.txt"
            cmd = [
                str(DEFAULT_PYTHON),
                str(BENCHMARKS_DIR / "benchmark_translation.py"),
                "--base-url",
                args.base_url,
                "--ds-email",
                args.ds_email,
                "--iterations",
                str(args.translation_iterations),
                "--warmup",
                str(args.translation_warmup),
                "--multi-subject-count",
                str(args.translation_multi_subject_count),
                "--json-out",
                str(json_path),
                "--csv-out",
                str(csv_path),
                "--txt-out",
                str(txt_path),
            ]
            add_value_arg(cmd, "--ds-password", args.ds_password)
            add_value_arg(cmd, "--home-uuid", args.home_uuid)
            if args.skip_refresh:
                cmd.append("--skip-refresh")
        elif benchmark_name == "petrinet":
            json_path = output_dir / "petrinet-benchmark.json"
            csv_path = output_dir / "petrinet-benchmark.csv"
            txt_path = output_dir / "petrinet-benchmark.txt"
            cmd = [
                str(DEFAULT_PYTHON),
                str(BENCHMARKS_DIR / "benchmark_petrinet.py"),
                "--rule-counts",
                *(str(count) for count in args.petrinet_rule_counts),
                "--iterations",
                str(args.petrinet_iterations),
                "--warmup",
                str(args.petrinet_warmup),
                "--conflict-type",
                args.petrinet_conflict_type,
                "--json-out",
                str(json_path),
                "--csv-out",
                str(csv_path),
                "--txt-out",
                str(txt_path),
            ]
        elif benchmark_name == "owl":
            json_path = output_dir / "owl-loading-benchmark.json"
            csv_path = output_dir / "owl-loading-benchmark.csv"
            txt_path = output_dir / "owl-loading-benchmark.txt"
            cmd = [
                str(DEFAULT_PYTHON),
                str(BENCHMARKS_DIR / "benchmark_owl_loading.py"),
                "--ontology-directory",
                args.owl_ontology_directory,
                "--ontology-file",
                args.owl_ontology_file,
                "--iterations",
                str(args.owl_iterations),
                "--warmup",
                str(args.owl_warmup),
                "--json-out",
                str(json_path),
                "--csv-out",
                str(csv_path),
                "--txt-out",
                str(txt_path),
            ]
            if args.owl_suppress_reasoner_output:
                cmd.append("--suppress-reasoner-output")
        else:
            json_path = output_dir / "api-benchmark.json"
            csv_path = output_dir / "api-benchmark.csv"
            txt_path = output_dir / "api-benchmark.txt"
            cmd = [
                str(DEFAULT_PYTHON),
                str(BENCHMARKS_DIR / "benchmark_api_collection.py"),
                "--base-url",
                args.api_collection_base_url,
                "--collection",
                str(Path(args.api_collection).expanduser().resolve()),
                "--iterations",
                str(args.api_iterations),
                "--json-out",
                str(json_path),
                "--csv-out",
                str(csv_path),
                "--txt-out",
                str(txt_path),
                "--dc-email",
                args.dc_email,
                "--dc-password",
                args.dc_password,
                "--ds-email",
                args.ds_email,
                "--delegate-email",
                args.delegate_email,
                "--dpo-email",
                args.dpo_email,
                "--dpo-password",
                args.dpo_password,
                "--marketplace-integration-token",
                args.marketplace_integration_token,
                "--dc-updated-password",
                args.dc_updated_password,
                "--dpo-updated-email",
                args.dpo_updated_email,
                "--dpo-updated-password",
                args.dpo_updated_password,
            ]
            add_value_arg(cmd, "--ds-password", args.ds_password)
            if args.api_success_only:
                cmd.append("--success-only")

        print()
        print(f"=== Running {benchmark_name} ===")
        benchmark_runs.append(run_benchmark(benchmark_name, cmd))
        artifact_paths[benchmark_name] = {
            "json": json_path,
            "csv": csv_path,
            "txt": txt_path,
        }
        reports[benchmark_name] = load_report_if_exists(json_path)

    summary_lines = build_summary_lines(
        output_dir=output_dir,
        selected_benchmarks=selected_benchmarks,
        benchmark_runs=benchmark_runs,
        reports=reports,
        artifact_paths=artifact_paths,
    )
    summary_path = dump_text_report(summary_lines, output_dir / "summary.txt")
    print()
    print(f"Summary written to {summary_path}")

    if any(run["status"] != "ok" for run in benchmark_runs):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
