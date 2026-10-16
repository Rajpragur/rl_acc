"""Render a short animated view of a recorded ACC simulation trace."""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1280, 720
NAVY = (14, 24, 38)
PANEL = (26, 39, 56)
ASPHALT = (39, 48, 60)
WHITE = (238, 244, 249)
MUTED = (153, 170, 188)
CYAN = (52, 211, 190)
AMBER = (247, 174, 76)
RED = (241, 105, 105)
GRID = (55, 70, 88)


def font(size: int, bold: bool = False):
    paths = [
        "/System/Library/Fonts/Supplemental/Verdana Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Verdana.ttf",
        "/System/Library/Fonts/SFCompact.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                pass
    return ImageFont.load_default()


def load_trace(path: Path, scenario: str, controller: str) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)
                if r["scenario"] == scenario and r["controller"] == controller]
    if not rows:
        raise ValueError(f"No trace for {controller!r} in scenario {scenario!r} at {path}")
    fields = ["t", "gap", "desired_gap", "ego_speed", "lead_speed", "command",
              "acceleration", "jerk", "rss_margin", "intervention"]
    for row in rows:
        for k in fields:
            row[k] = float(row[k])
    return rows


def draw_car(draw: ImageDraw.ImageDraw, x: float, y: int, color: tuple,
             label: str, fnt):
    x = int(max(60, min(W - 165, x)))
    draw.rounded_rectangle((x, y + 12, x + 105, y + 62), radius=14,
                           fill=color, outline=(230, 238, 245), width=2)
    draw.polygon([(x + 21, y + 12), (x + 37, y - 3),
                  (x + 77, y - 3), (x + 91, y + 12)], fill=color)
    draw.rounded_rectangle((x + 39, y + 1, x + 75, y + 11), radius=4,
                           fill=(195, 218, 225))
    draw.ellipse((x + 17, y + 51, x + 42, y + 75), fill=(7, 12, 20))
    draw.ellipse((x + 70, y + 51, x + 95, y + 75), fill=(7, 12, 20))
    draw.text((x + 4, y + 82), label, font=fnt, fill=WHITE)


def render_frame(rows: list[dict], idx: int, path: Path, scenario: str, controller: str):
    row = rows[idx]
    image = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(image)
    f_title, f_body, f_small, f_label = font(28, True), font(19), font(15), font(17, True)

    d.text((54, 26), "Adaptive cruise control", font=f_title, fill=WHITE)
    d.text((54, 66), f"{scenario.replace('_', ' ').title()} | {controller}", font=f_body, fill=MUTED)
    d.text((900, 36), "10 Hz SIMULATION", font=f_label, fill=CYAN)

    # Two-car road scene.
    d.rounded_rectangle((48, 112, 1232, 355), radius=18, fill=PANEL)
    road_y0, road_y1 = 190, 320
    d.rectangle((72, road_y0, 1208, road_y1), fill=ASPHALT)
    d.line((72, road_y0 + 8, 1208, road_y0 + 8), fill=(110, 124, 140), width=2)
    d.line((72, road_y1 - 8, 1208, road_y1 - 8), fill=(110, 124, 140), width=2)
    for x in range(92, 1190, 74):
        d.rounded_rectangle((x, 250, x + 40, 255), radius=2, fill=(187, 198, 207))
    y_car = 216
    ego_x = 320
    scale = 7.0
    lead_x = ego_x + 105 + max(8.0, row["gap"]) * scale
    draw_car(d, ego_x, y_car, CYAN, "EGO", f_label)
    draw_car(d, lead_x, y_car, AMBER, "LEAD", f_label)
    x_gap_start = ego_x + 106
    x_gap_end = max(x_gap_start + 24, min(lead_x, W - 78))
    d.line((x_gap_start, y_car + 37, x_gap_end, y_car + 37), fill=WHITE, width=2)
    d.line((x_gap_start, y_car + 29, x_gap_start, y_car + 44), fill=WHITE, width=2)
    d.line((x_gap_end, y_car + 29, x_gap_end, y_car + 44), fill=WHITE, width=2)
    d.rounded_rectangle((520, 125, 788, 176), radius=11, fill=(12, 20, 32))
    d.text((540, 139), f"GAP  {row['gap']:.1f} m", font=f_label, fill=WHITE)

    # Live measurements; the high minimum spacing is visible during the brake event.
    metrics = [
        ("EGO SPEED", f"{row['ego_speed']:.1f} m/s"),
        ("LEAD SPEED", f"{row['lead_speed']:.1f} m/s"),
        ("TARGET GAP", f"{row['desired_gap']:.1f} m"),
        ("FILTER", "INTERVENED" if row["intervention"] else "PASS THROUGH"),
    ]
    bx = 54
    for label, val in metrics:
        d.text((bx, 372), label, font=f_small, fill=MUTED)
        color = RED if label == "FILTER" and row["intervention"] else WHITE
        d.text((bx, 396), val, font=f_label, fill=color)
        bx += 294

    # Gap history against the desired time-gap policy.
    d.rounded_rectangle((48, 438, 1232, 672), radius=18, fill=PANEL)
    d.text((76, 454), "Following distance", font=f_label, fill=WHITE)
    d.line((970, 466, 1004, 466), fill=CYAN, width=4)
    d.text((1013, 456), "measured", font=f_small, fill=MUTED)
    d.line((1092, 466, 1126, 466), fill=AMBER, width=4)
    d.text((1134, 456), "target", font=f_small, fill=MUTED)
    plot = (96, 500, 1196, 634)
    x0, y0, x1, y1 = plot
    for val in (0, 15, 30, 45, 60):
        yy = y1 - (val / 60) * (y1 - y0)
        d.line((x0, int(yy), x1, int(yy)), fill=GRID, width=1)
        d.text((60, int(yy) - 8), str(val), font=f_small, fill=MUTED)
    d.text((55, 480), "m", font=f_small, fill=MUTED)
    total = max(1, len(rows) - 1)
    def xy(i: int, value: float):
        x = x0 + (x1 - x0) * i / total
        y = y1 - (max(0.0, min(60.0, value)) / 60.0) * (y1 - y0)
        return (int(x), int(y))
    gap_pts = [xy(i, r["gap"]) for i, r in enumerate(rows[:idx + 1])]
    target_pts = [xy(i, r["desired_gap"]) for i, r in enumerate(rows[:idx + 1])]
    if len(gap_pts) > 1:
        d.line(gap_pts, fill=CYAN, width=4)
        d.line(target_pts, fill=AMBER, width=3)
    current_x = x0 + (x1 - x0) * idx / total
    d.line((int(current_x), y0, int(current_x), y1), fill=WHITE, width=2)
    current_y = xy(idx, row["gap"])[1]
    d.ellipse((int(current_x) - 6, current_y - 6, int(current_x) + 6, current_y + 6), fill=CYAN)
    d.text((x0, 642), "0 s", font=f_small, fill=MUTED)
    d.text((x1 - 46, 642), f"{rows[-1]['t']:.0f} s", font=f_small, fill=MUTED)
    d.text((1080, 642), f"t = {row['t']:.1f} s", font=f_small, fill=WHITE)
    d.text((54, 686), "Point-mass model | Results are simulated, not road-test data", font=f_small, fill=MUTED)
    image.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", default="brake", choices=["steady", "wave", "brake", "cut_in", "emergency"])
    parser.add_argument("--controller", default="Q+RSS", choices=["Q-Learning", "Q+RSS", "CTG-PID", "MPC"])
    parser.add_argument("--trace", default="outputs/representative_traces.csv")
    parser.add_argument("--output", default="outputs/ACC_Brake_Simulation.mp4")
    args = parser.parse_args()
    rows = load_trace(Path(args.trace), args.scenario, args.controller)
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to encode the MP4")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="acc_frames_") as temp:
        frame_dir = Path(temp)
        for idx in range(len(rows)):
            render_frame(rows, idx, frame_dir / f"frame_{idx:04d}.png", args.scenario, args.controller)
        subprocess.run([
            ffmpeg, "-y", "-loglevel", "error", "-framerate", "20",
            "-i", str(frame_dir / "frame_%04d.png"), "-c:v", "libx264",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output),
        ], check=True)
    print(f"Saved {len(rows)} frames to {output} ({len(rows) / 20:.1f} s at 2x simulation speed).")


if __name__ == "__main__":
    main()
