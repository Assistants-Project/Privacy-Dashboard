from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Callable

from common import append_section, dump_csv_rows, dump_json_report, dump_text_report, stats_block_lines, summarize_ms


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.models.entities.sifis.owl.action import Action  # noqa: E402
from app.models.entities.sifis.owl.rule import Rule  # noqa: E402
from app.models.entities.sifis.owl.trigger import Trigger  # noqa: E402
from app.services.petrinet_service import PetriNetService  # noqa: E402


def build_rule(trigger_idx: int, action_idx: int, *, effect: str, db_id: int) -> Rule:
    trigger = Trigger(
        url=f"https://benchmark.local/trigger#{trigger_idx}",
        id=f"trigger_{trigger_idx}",
        name=f"Trigger {trigger_idx}",
    )
    action = Action(
        url=f"https://benchmark.local/action#{action_idx}",
        id=f"action_{action_idx}",
        name=f"Action {action_idx}",
    )
    return Rule(
        db_id=db_id,
        effect=effect,
        subject="benchmark-subject@example.com",
        trigger=trigger,
        action=action,
        type="sifis",
    )


def build_ruleset(rule_count: int, conflict_type: str) -> tuple[Rule, list[Rule]]:
    if rule_count < 2:
        raise ValueError("rule_count must be >= 2")

    existing_rules: list[Rule] = []

    conflicting_effect = "permit" if conflict_type == "inconsistency" else "deny"
    existing_rules.append(build_rule(0, 0, effect=conflicting_effect, db_id=1))

    for index in range(1, rule_count):
        existing_rules.append(
            build_rule(index, index, effect="deny", db_id=index + 1)
        )

    target_rule = build_rule(
        0,
        0,
        effect="deny",
        db_id=10_000 + rule_count,
    )
    return target_rule, existing_rules


def benchmark_rule_count(
    *,
    log: Callable[[str], None],
    service: PetriNetService,
    rule_count: int,
    conflict_type: str,
    warmup: int,
    iterations: int,
) -> dict[str, Any]:
    target_rule, existing_rules = build_ruleset(rule_count, conflict_type)
    total_runs = warmup + iterations
    measured_rows: list[dict[str, Any]] = []

    for run_index in range(total_runs):
        t0 = time.perf_counter_ns()
        result = service.check_rule(target_rule, existing_rules, f"benchmark-home-{rule_count}")
        elapsed_ms = (time.perf_counter_ns() - t0) / 1_000_000.0
        phase = "warmup" if run_index < warmup else "measured"
        inconsistent_count = len(result.get("inconsistentRules", []) or [])
        redundant_count = len(result.get("redundantRules", []) or [])
        loop_count = len(result.get("loops", []) or [])
        log(
            f"[{phase}] rules={rule_count:03d} run={run_index + 1:02d} "
            f"check_ms={elapsed_ms:.3f} "
            f"inconsistent={inconsistent_count} redundant={redundant_count} loops={loop_count}"
        )
        if phase == "measured":
            measured_rows.append(
                {
                    "run_index": run_index + 1,
                    "check_ms": elapsed_ms,
                    "inconsistent_rules": inconsistent_count,
                    "redundant_rules": redundant_count,
                    "loops": loop_count,
                }
            )

    values = [float(item["check_ms"]) for item in measured_rows]
    stats = summarize_ms(values)
    log("")
    for line in stats_block_lines(f"rules={rule_count} check_rule latency", stats):
        log(line)
    log("")
    return {
        "rule_count": rule_count,
        "stats": stats,
        "runs": measured_rows,
        "conflict_type": conflict_type,
        "dataset_notes": [
            "One existing rule shares the same trigger/action pair as the target rule.",
            "Remaining rules are unique trigger/action pairs to scale net size without introducing extra conflicts.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark SCPN/Petri-net conflict detection time by measuring "
            "PetriNetService.check_rule() on synthetic rulesets."
        )
    )
    parser.add_argument(
        "--rule-counts",
        nargs="+",
        type=int,
        default=[10, 25, 50],
    )
    parser.add_argument("--iterations", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument(
        "--conflict-type",
        choices=("inconsistency", "redundancy"),
        default="inconsistency",
    )
    parser.add_argument("--json-out")
    parser.add_argument("--csv-out")
    parser.add_argument("--txt-out")
    args = parser.parse_args()

    if args.iterations < 1:
        raise SystemExit("--iterations must be >= 1")
    if args.warmup < 0:
        raise SystemExit("--warmup must be >= 0")
    if any(count < 2 for count in args.rule_counts):
        raise SystemExit("All --rule-counts must be >= 2")

    terminal_lines: list[str] = []

    def log(message: str = "") -> None:
        print(message)
        terminal_lines.append(message)

    service = PetriNetService(owl_service=None)
    curve = []

    for rule_count in args.rule_counts:
        curve.append(
            benchmark_rule_count(
                log=log,
                service=service,
                rule_count=rule_count,
                conflict_type=args.conflict_type,
                warmup=args.warmup,
                iterations=args.iterations,
            )
        )

    report = {
        "benchmark": "scpn_conflict_detection_time",
        "rule_counts": args.rule_counts,
        "iterations": args.iterations,
        "warmup": args.warmup,
        "conflict_type": args.conflict_type,
        "curve": curve,
        "notes": [
            "This microbenchmark measures the Python service directly, without HTTP or database overhead.",
            "It exercises structural conflict detection and Petri-net construction. Trigger implication/loop reasoning is intentionally excluded from the synthetic dataset.",
        ],
    }

    if args.json_out:
        json_path = dump_json_report(report, args.json_out)
        log(f"JSON report written to {json_path}")
    if args.csv_out:
        csv_rows = [
            {
                "rule_count": bucket["rule_count"],
                "conflict_type": bucket["conflict_type"],
                "run_index": run["run_index"],
                "check_ms": run["check_ms"],
                "inconsistent_rules": run["inconsistent_rules"],
                "redundant_rules": run["redundant_rules"],
                "loops": run["loops"],
            }
            for bucket in curve
            for run in bucket["runs"]
        ]
        csv_path = dump_csv_rows(
            [
                "rule_count",
                "conflict_type",
                "run_index",
                "check_ms",
                "inconsistent_rules",
                "redundant_rules",
                "loops",
            ],
            csv_rows,
            args.csv_out,
        )
        log(f"CSV report written to {csv_path}")
    if args.txt_out:
        txt_lines: list[str] = []
        append_section(
            txt_lines,
            "SCPN Conflict Detection Time",
            [
                "Execution mode : direct Python service call",
                f"Conflict type : {args.conflict_type}",
                f"Measured runs : {args.iterations}",
                f"Warmup runs   : {args.warmup}",
                f"Rule counts   : {', '.join(str(count) for count in args.rule_counts)}",
            ],
        )
        curve_summary = [
            f"{bucket['rule_count']} -> median {bucket['stats']['median_ms']:.3f} ms, "
            f"mean {bucket['stats']['mean_ms']:.3f} ms, p95 {bucket['stats']['p95_ms']:.3f} ms"
            for bucket in curve
        ]
        append_section(txt_lines, "Curve summary", curve_summary)
        for bucket in curve:
            body = [
                f"conflict_type      : {bucket['conflict_type']}",
                *stats_block_lines("", bucket["stats"])[1:],
                *bucket.get("dataset_notes", []),
            ]
            append_section(txt_lines, f"rules={bucket['rule_count']}", body)
        append_section(txt_lines, "Notes", report["notes"])
        txt_path = dump_text_report(txt_lines, args.txt_out)
        print(f"TXT report written to {txt_path}")


if __name__ == "__main__":
    main()
