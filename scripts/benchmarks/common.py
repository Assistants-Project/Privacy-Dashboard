from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable, Sequence

TESTING_ONLY_DS_PASSWORD = "testing-only-password"


def ensure_parent_dir(path: str | Path) -> Path:
    resolved = Path(path).expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    return resolved


def percentile(values: Sequence[float], p: float) -> float:
    if not values:
        raise ValueError("Cannot compute percentile of an empty sequence")
    if p < 0 or p > 100:
        raise ValueError("Percentile must be between 0 and 100")

    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]

    rank = (len(ordered) - 1) * (p / 100.0)
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]

    weight = rank - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def summarize_ms(values_ms: Sequence[float]) -> dict[str, float | int]:
    if not values_ms:
        raise ValueError("Cannot summarize an empty sequence")

    return {
        "count": len(values_ms),
        "min_ms": min(values_ms),
        "max_ms": max(values_ms),
        "mean_ms": statistics.fmean(values_ms),
        "median_ms": statistics.median(values_ms),
        "p95_ms": percentile(values_ms, 95.0),
        "stdev_ms": statistics.stdev(values_ms) if len(values_ms) > 1 else 0.0,
    }


def dump_json_report(payload: dict[str, Any], path: str | Path) -> Path:
    resolved = ensure_parent_dir(path)
    resolved.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    return resolved


def dump_csv_rows(fieldnames: Sequence[str], rows: Iterable[dict[str, Any]], path: str | Path) -> Path:
    resolved = ensure_parent_dir(path)
    with resolved.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return resolved


def stats_block_lines(title: str, stats: dict[str, float | int]) -> list[str]:
    return [
        title,
        f"  count     : {stats['count']}",
        f"  min_ms    : {stats['min_ms']:.3f}",
        f"  max_ms    : {stats['max_ms']:.3f}",
        f"  mean_ms   : {stats['mean_ms']:.3f}",
        f"  median_ms : {stats['median_ms']:.3f}",
        f"  p95_ms    : {stats['p95_ms']:.3f}",
        f"  stdev_ms  : {stats['stdev_ms']:.3f}",
    ]


def print_stats_block(title: str, stats: dict[str, float | int]) -> None:
    for line in stats_block_lines(title, stats):
        print(line)


def append_section(lines: list[str], title: str, body: Sequence[str] | None = None) -> None:
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(title)
    if body:
        lines.extend(body)


def dump_text_report(lines: str | Sequence[str], path: str | Path) -> Path:
    resolved = ensure_parent_dir(path)
    if isinstance(lines, str):
        content = lines
    else:
        content = "\n".join(lines)
    if content and not content.endswith("\n"):
        content += "\n"
    resolved.write_text(content, encoding="utf-8")
    return resolved


def resolve_ds_password(provided_password: str | None) -> tuple[str, bool]:
    if provided_password:
        return provided_password, False
    return TESTING_ONLY_DS_PASSWORD, True


def ds_password_fallback_error(script_name: str) -> str:
    return (
        f"{script_name} could not authenticate with the testing-only Data Subject password fallback. "
        "That fallback works only when the backend runs with FLASK_ENV=testing. "
        "Against development/demo, rerun with --ds-password <real Smartotum password>."
    )
