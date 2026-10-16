"""Summarize a small, attributed OpenACC commercial-ACC field reference."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/openacc/JRC-VC_260219_part2.csv")
    parser.add_argument("--output", default="outputs/openacc_reference.json")
    args = parser.parse_args()

    source = Path(args.input)
    with source.open(newline="", encoding="utf-8-sig") as f:
        for _ in range(5):
            next(f)
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            if row.get("Driver1") != "Human" or row.get("Driver2") != "ACC":
                continue
            try:
                vals = [float(row[k]) for k in ("Time", "Speed1", "Speed2", "IVS1")]
            except (KeyError, TypeError, ValueError):
                continue
            rows.append(vals)

    data = np.asarray(rows, dtype=float)
    valid = (np.isfinite(data).all(axis=1) & (data[:, 2] > 5.0)
             & (data[:, 3] > 0.0) & (data[:, 3] < 150.0))
    data = data[valid]
    if len(data) == 0:
        raise ValueError("No valid Human-lead / ACC-follower observations found")

    time, lead_speed, follower_speed, gap = data.T
    headway = gap / follower_speed
    median_follower_speed = float(np.median(follower_speed))
    target_gap = 5.0 + 1.3 * median_follower_speed
    reference = {
        "dataset": "Open ACC Database / OpenACC",
        "provider": "European Commission Joint Research Centre",
        "doi": "10.2905/JRC.KMH3D00",
        "paper_doi": "10.1016/j.trc.2021.103047",
        "campaign": "Vicolungo, 2019-02-26",
        "recording": source.name,
        "leader": "Mitsubishi SpaceStar (Human driver)",
        "follower": "Ford S-Max (ACC active)",
        "distance_setting": "minimum",
        "observations": int(len(data)),
        "duration_s": float(time[-1] - time[0]),
        "sample_rate_note": "The campaign notes say GNSS was originally sampled at about 3–5 Hz and spline-interpolated to 10 Hz.",
        "follower_speed_mps_median": median_follower_speed,
        "leader_speed_mps_median": float(np.median(lead_speed)),
        "bumper_gap_m_median": float(np.median(gap)),
        "bumper_gap_m_p10": float(np.quantile(gap, 0.10)),
        "bumper_gap_m_p90": float(np.quantile(gap, 0.90)),
        "time_headway_s_mean": float(np.mean(headway)),
        "time_headway_s_median": float(np.median(headway)),
        "time_headway_s_p10": float(np.quantile(headway, 0.10)),
        "time_headway_s_p90": float(np.quantile(headway, 0.90)),
        "project_target_at_median_speed_m": target_gap,
        "project_target_effective_headway_s": float(target_gap / median_follower_speed),
        "interpretation": "Descriptive real-road context from one minimum-distance commercial ACC run. It is not a same-condition cut-in head-to-head or evidence about all current ACC systems.",
        "data_url": "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/TransportExpData/JRCDBT0001/LATEST/Vicolungo/JRC-VC_260219_part2.csv",
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(reference, indent=2), encoding="utf-8")
    print(json.dumps(reference, indent=2))


if __name__ == "__main__":
    main()
