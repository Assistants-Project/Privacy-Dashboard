from __future__ import annotations

import argparse
import io
import sys
import time
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, Callable

from common import (
    append_section,
    dump_csv_rows,
    dump_json_report,
    dump_text_report,
    stats_block_lines,
    summarize_ms,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import BaseConfig  # noqa: E402
from app.services.owl_service import OWLService  # noqa: E402


def resolve_default_ontology_directory() -> str:
    configured = Path(BaseConfig.ONTOLOGY_DIRECTORY)
    candidates = [
        configured,
        BACKEND_DIR / configured,
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(BACKEND_DIR / configured)


def benchmark_owl_loading(
    *,
    log: Callable[[str], None],
    ontology_directory: str,
    ontology_file: str,
    warmup: int,
    iterations: int,
    suppress_reasoner_output: bool,
) -> dict[str, Any]:
    cfg = {
        "ONTOLOGY_DIRECTORY": ontology_directory,
        "ONTOLOGY_SIFIS_FILE": ontology_file,
        "LOGGING_LEVEL": "ERROR",
    }

    total_runs = warmup + iterations
    measured_rows: list[dict[str, Any]] = []

    for run_index in range(total_runs):
        t0 = time.perf_counter_ns()
        if suppress_reasoner_output:
            sink = io.StringIO()
            with redirect_stdout(sink), redirect_stderr(sink):
                service = OWLService(cfg)
        else:
            service = OWLService(cfg)
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0

        phase = "warmup" if run_index < warmup else "measured"
        log(
            f"[{phase}] run={run_index + 1:02d} "
            f"owl_init_ms={elapsed_ms:.3f} "
            f"ontology={ontology_file}"
        )

        if phase == "measured":
            measured_rows.append(
                {
                    "run_index": run_index + 1,
                    "owl_init_ms": elapsed_ms,
                    "ontology_directory": ontology_directory,
                    "ontology_file": ontology_file,
                }
            )

        del service

    stats = summarize_ms([float(item["owl_init_ms"]) for item in measured_rows])
    log("")
    for line in stats_block_lines("OWL ontology loading latency", stats):
        log(line)
    log("")

    return {
        "benchmark": "owl_ontology_loading_time",
        "ontology_directory": ontology_directory,
        "ontology_file": ontology_file,
        "warmup": warmup,
        "iterations": iterations,
        "suppress_reasoner_output": suppress_reasoner_output,
        "stats": stats,
        "runs": measured_rows,
        "notes": [
            "This microbenchmark measures OWLService initialization directly in Python.",
            "It includes base ontology loading and HermiT reasoner startup used by the PTP stack.",
            "It does not include Flask app startup, Docker container startup, or home ontology regeneration.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark OWL ontology loading time by measuring OWLService "
            "initialization used by the PTP stack."
        )
    )
    parser.add_argument(
        "--ontology-directory",
        default=resolve_default_ontology_directory(),
        help="Ontology directory passed to OWLService. Default: backend-resolved BaseConfig.ONTOLOGY_DIRECTORY",
    )
    parser.add_argument(
        "--ontology-file",
        default=BaseConfig.ONTOLOGY_SIFIS_FILE,
        help="Base ontology filename passed to OWLService. Default: BaseConfig.ONTOLOGY_SIFIS_FILE",
    )
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument(
        "--suppress-reasoner-output",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Suppress OWLready/HermiT stdout/stderr during timed initialization. Default: enabled.",
    )
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

    report = benchmark_owl_loading(
        log=log,
        ontology_directory=args.ontology_directory,
        ontology_file=args.ontology_file,
        warmup=args.warmup,
        iterations=args.iterations,
        suppress_reasoner_output=args.suppress_reasoner_output,
    )

    if args.json_out:
        json_path = dump_json_report(report, args.json_out)
        log(f"JSON report written to {json_path}")

    if args.csv_out:
        csv_path = dump_csv_rows(
            [
                "run_index",
                "owl_init_ms",
                "ontology_directory",
                "ontology_file",
            ],
            report["runs"],
            args.csv_out,
        )
        log(f"CSV report written to {csv_path}")

    if args.txt_out:
        txt_lines: list[str] = []
        append_section(
            txt_lines,
            "OWL Ontology Loading Time",
            [
                f"Ontology directory       : {report['ontology_directory']}",
                f"Ontology file            : {report['ontology_file']}",
                f"Measured runs            : {report['iterations']}",
                f"Warmup runs              : {report['warmup']}",
                f"Suppress reasoner output : {report['suppress_reasoner_output']}",
            ],
        )
        append_section(
            txt_lines,
            "Aggregate stats",
            stats_block_lines("", report["stats"])[1:],
        )
        append_section(txt_lines, "Notes", report["notes"])
        txt_path = dump_text_report(txt_lines, args.txt_out)
        print(f"TXT report written to {txt_path}")


if __name__ == "__main__":
    main()
