"""Evaluate ACC controllers on matched, randomized scenarios."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from acc_sim import QAgent, run_episode, string_stability_test


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict], numeric: list[str]) -> dict:
    """Return episode means, sample SDs, and approximate 95% CIs."""
    result = {"episodes": len(rows)}
    for key in numeric:
        vals = np.asarray([r[key] for r in rows], dtype=float)
        vals = vals[np.isfinite(vals)]
        n = len(vals)
        mean = float(np.mean(vals)) if n else float("nan")
        sd = float(np.std(vals, ddof=1)) if n > 1 else 0.0
        # Normal approximation is adequate for the default n=50. The interval is
        # descriptive; it is not a significance test or a road-risk estimate.
        half = 1.96 * sd / math.sqrt(n) if n > 1 else 0.0
        result[key + "_mean"] = mean
        result[key + "_sd"] = sd
        # All episode-level measures in this project have a nonnegative support;
        # keep the displayed interval inside that range.
        result[key + "_ci95_low"] = max(0.0, mean - half) if n else float("nan")
        upper = min(100.0, mean + half) if key == "ttc_below_2s_pct" else mean + half
        result[key + "_ci95_high"] = upper if n else float("nan")
        result[key + "_valid_n"] = n
    return result


def paired_differences(rows: list[dict], metrics: list[str],
                       comparisons: list[tuple[str, str]]) -> list[dict]:
    by_key = {(r["scenario"], r["seed"], r["controller"]): r for r in rows}
    scenarios = sorted({r["scenario"] for r in rows})
    result = []
    for scenario in scenarios:
        for controller_a, controller_b in comparisons:
            for metric in metrics:
                diffs = []
                for seed in sorted({r["seed"] for r in rows if r["scenario"] == scenario}):
                    a = by_key.get((scenario, seed, controller_a))
                    b = by_key.get((scenario, seed, controller_b))
                    if a is None or b is None:
                        continue
                    av, bv = float(a[metric]), float(b[metric])
                    if np.isfinite(av) and np.isfinite(bv):
                        diffs.append(av - bv)
                if not diffs:
                    continue
                vals = np.asarray(diffs, dtype=float)
                sd = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
                half = 1.96 * sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
                result.append({
                    "scenario": scenario,
                    "controller_a": controller_a,
                    "controller_b": controller_b,
                    "metric": metric,
                    "paired_delta_a_minus_b_mean": float(np.mean(vals)),
                    "paired_delta_sd": sd,
                    "ci95_low": float(np.mean(vals) - half),
                    "ci95_high": float(np.mean(vals) + half),
                    "paired_episodes": len(vals),
                    "interval_method": "normal approximation on paired per-seed differences",
                })
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/q_agent.npz")
    parser.add_argument("--output", default="outputs/formal_50seed")
    parser.add_argument("--seeds", type=int, default=50)
    args = parser.parse_args()
    if args.seeds < 1:
        parser.error("--seeds must be at least 1")

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    model = QAgent(np.load(args.model)["q_table"])
    scenarios = ["steady", "wave", "brake", "cut_in", "emergency"]
    controllers = ["CTG-PID", "MPC", "Q-Learning", "Q+RSS"]
    trace_seed = min(17, args.seeds - 1)
    raw: list[dict] = []
    traces: list[dict] = []
    for scenario in scenarios:
        for seed in range(args.seeds):
            for controller in controllers:
                result, trace = run_episode(controller, scenario, seed, model,
                                            record=(seed == trace_seed))
                raw.append(result)
                if seed == trace_seed:
                    traces.extend({"controller": controller, "scenario": scenario, **row}
                                  for row in trace)

    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in raw:
        grouped[(row["scenario"], row["controller"])].append(row)
    aggregate: list[dict] = []
    numeric = ["gap_rmse_m", "mean_abs_jerk_mps3", "rms_jerk_mps3", "min_ttc_s",
               "ttc_below_2s_pct", "min_gap_m", "collision", "rss_interventions",
               "rss_intervention_pct", "min_command_margin_m", "mean_decision_ms"]
    for (scenario, controller), rows in sorted(grouped.items()):
        row = {"scenario": scenario, "controller": controller, "episodes": len(rows)}
        row.update(summarize(rows, numeric))
        aggregate.append(row)

    id_rows = [r for r in raw if r["scenario"] in {"steady", "wave", "brake"}]
    ood_rows = [r for r in raw if r["scenario"] in {"cut_in", "emergency"}]
    overall: list[dict] = []
    for label, rows in [("in_distribution", id_rows), ("holdout_ood", ood_rows)]:
        for controller in controllers:
            subset = [r for r in rows if r["controller"] == controller]
            row = {"group": label, "controller": controller}
            row.update(summarize(subset, numeric))
            overall.append(row)

    paired = paired_differences(
        raw,
        ["gap_rmse_m", "mean_abs_jerk_mps3", "min_gap_m", "ttc_below_2s_pct", "collision"],
        [("Q+RSS", "Q-Learning"), ("Q-Learning", "CTG-PID"), ("Q-Learning", "MPC")],
    )
    string_rows = [string_stability_test(c, model) for c in controllers]
    write_csv(out / "episode_metrics.csv", raw)
    write_csv(out / "scenario_summary.csv", aggregate)
    write_csv(out / "group_summary.csv", overall)
    write_csv(out / "paired_differences.csv", paired)
    write_csv(out / "representative_traces.csv", traces)
    (out / "string_stability.json").write_text(json.dumps(string_rows, indent=2), encoding="utf-8")
    manifest = {
        "model": args.model,
        "seeds_per_cell": args.seeds,
        "representative_trace_seed": trace_seed,
        "in_distribution_scenarios": ["steady", "wave", "brake"],
        "holdout_ood_scenarios": ["cut_in", "emergency"],
        "controllers": controllers,
        "episodes": len(raw),
        "dt_s": 0.1,
        "episode_horizon_s": 40.0,
        "seed_range": list(range(args.seeds)),
        "scenario_randomization": {
            "steady_wave_brake": "Initial speed, lead speed and/or phase/gap vary by seed within profiles represented during training; moderate brake shape matches the training profile.",
            "cut_in": "Synthetic instantaneous gap drop of 16–26 m, event onset 6–10 s, followed by 3.5–5.0 m/s^2 lead braking for 2–3 s.",
            "emergency": "Higher-speed holdout; onset 5.5–9 s, 5.5–8.0 m/s^2 lead braking for 1.5–2.4 s.",
            "matching": "Each controller receives the same per-seed initial state and event parameters.",
        },
        "intervals": "Approximate 95% normal intervals over episode means; paired_differences.csv uses matched per-seed differences. Descriptive intervals only, not significance tests.",
        "commercial_reference": "One Vicolungo OpenACC field trace is summarized separately as context; it is not a same-condition cut-in head-to-head.",
        "notes": "The cut-in and emergency holdout families were excluded from tabular Q-learning training. This is a simplified scripted point-mass simulator, not a vehicle validation. The cut-in uses an instantaneous longitudinal gap change without lane-change geometry or perception.",
    }
    (out / "experiment_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"episodes": len(raw), "summary": str(out / "group_summary.csv"),
                      "cut_in_paired_differences": str(out / "paired_differences.csv"),
                      "string_stability": string_rows}, indent=2))


if __name__ == "__main__":
    main()
