"""Render a presentation-ready ACC cut-in comparison from recorded project traces.

The film is a silent, data-driven 16:9 explainer. Its vehicle graphic is explicitly
longitudinal: the simulated cut-in is an instantaneous gap change, not lane geometry.
Requires Pillow and FFmpeg; all frames are streamed to FFmpeg to keep memory use low.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H, FPS = 1920, 1080, 24
INK = (8, 15, 29)
PANEL = (17, 28, 45)
PANEL_2 = (22, 35, 54)
WHITE = (241, 246, 252)
MUTED = (153, 171, 192)
FAINT = (90, 110, 135)
GRID = (40, 57, 79)
CYAN = (77, 220, 205)
VIOLET = (179, 149, 255)
AMBER = (255, 190, 105)
RED = (255, 112, 130)
BLUE = (102, 168, 255)
GREEN = (115, 225, 166)

TRACE_COLORS = {"Q-Learning": VIOLET, "Q+RSS": CYAN, "MPC": AMBER}
DISPLAY_NAMES = {
    "Q-Learning": ("Q-LEARNING", "learned correction on classical ACC"),
    "Q+RSS": ("Q + BRAKING GUARD", "learned correction with action filter"),
    "MPC": ("PREDICTIVE MPC", "short-horizon optimization reference"),
}

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_MONO = Path("/System/Library/Fonts/Menlo.ttc")


def font(size: int, bold: bool = False, mono: bool = False):
    path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REGULAR)
    if path.exists():
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            pass
    return ImageFont.load_default()


F = {
    (size, bold, mono): font(size, bold, mono)
    for size in (17, 19, 20, 22, 24, 26, 28, 30, 32, 36, 40, 44, 48, 54, 60, 66, 74, 84, 92, 104)
    for bold in (False, True)
    for mono in (False, True)
}


def ft(size: int, bold: bool = False, mono: bool = False):
    return F.get((size, bold, mono)) or font(size, bold, mono)


def txt(draw: ImageDraw.ImageDraw, xy, value: str, size: int, fill=WHITE,
        bold: bool = False, mono: bool = False, anchor=None):
    draw.text(xy, value, font=ft(size, bold, mono), fill=fill, anchor=anchor)


def centered(draw: ImageDraw.ImageDraw, x: int, y: int, value: str, size: int,
             fill=WHITE, bold: bool = False, mono: bool = False):
    txt(draw, (x, y), value, size, fill, bold, mono, anchor="mm")


def round_rect(draw, box, radius=22, fill=PANEL, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, box, label: str, color=CYAN, fill=(18, 37, 52), size=18):
    round_rect(draw, box, radius=22, fill=fill, outline=tuple(min(255, int(v * 0.62 + 40)) for v in color), width=2)
    txt(draw, (box[0] + 18, box[1] + (box[3] - box[1]) // 2), label,
        size, color, True, anchor="lm")


def make_background() -> Image.Image:
    image = Image.new("RGB", (W, H), INK)
    px = image.load()
    top = (13, 26, 44)
    bottom = (7, 13, 25)
    for y in range(H):
        p = y / (H - 1)
        color = tuple(round(top[k] * (1 - p) + bottom[k] * p) for k in range(3))
        for x in range(W):
            side = max(0.0, (x / W - 0.48) / 0.52)
            glow = max(0.0, 1.0 - abs(p - 0.27) * 3.2) * side
            px[x, y] = tuple(min(255, round(color[k] + glow * (4 if k == 1 else 8 if k == 2 else 2))) for k in range(3))
    d = ImageDraw.Draw(image)
    # Fine technical grid, concentrated at the edges so typography stays calm.
    for x in range(64, W, 72):
        d.line((x, 0, x, H), fill=(13, 24, 39), width=1)
    for y in range(50, H, 72):
        d.line((0, y, W, y), fill=(13, 24, 39), width=1)
    for x in range(56, W, 48):
        for y in range(42, H, 48):
            if (x // 48 + y // 48) % 4 == 0:
                d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(31, 49, 69))
    return image


BG = make_background()


def base_frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = BG.copy()
    return image, ImageDraw.Draw(image)


def footer(draw, left: str, right: str = "ACC CONTROL STUDY  /  01"):
    draw.line((76, 1014, W - 76, 1014), fill=(37, 54, 76), width=2)
    txt(draw, (78, 1034), left, 18, MUTED)
    txt(draw, (W - 78, 1034), right, 17, FAINT, mono=True, anchor="ra")


def header(draw, kicker: str, right: str = "REINFORCEMENT LEARNING  ×  AUTOMOTIVE CONTROL"):
    txt(draw, (82, 59), kicker.upper(), 20, CYAN, True, mono=True)
    txt(draw, (W - 84, 60), right, 16, MUTED, mono=True, anchor="ra")
    draw.line((82, 98, W - 82, 98), fill=(43, 61, 84), width=2)


def draw_car(draw, x: float, y: float, color, label: str, width=104, height=54):
    x, y = int(x), int(y)
    # Restrained vector silhouette; side-on on purpose because the model has no lane geometry.
    draw.rounded_rectangle((x, y + 17, x + width, y + height - 4), radius=15,
                           fill=color, outline=(228, 239, 249), width=2)
    draw.polygon([(x + 17, y + 18), (x + 34, y + 3), (x + width - 27, y + 3),
                  (x + width - 11, y + 18)], fill=color)
    draw.rounded_rectangle((x + 39, y + 7, x + width - 31, y + 17), radius=4,
                           fill=(161, 190, 208), outline=(211, 226, 237), width=1)
    for wx in (x + 17, x + width - 40):
        draw.ellipse((wx, y + height - 12, wx + 24, y + height + 12), fill=(5, 10, 19), outline=(106, 124, 143), width=2)
        draw.ellipse((wx + 7, y + height - 5, wx + 17, y + height + 5), fill=(97, 117, 139))
    draw.ellipse((x + width - 7, y + 29, x + width - 1, y + 39), fill=(255, 239, 190))
    draw.ellipse((x + 2, y + 29, x + 8, y + 39), fill=(RED))
    txt(draw, (x + width / 2, y + height + 30), label, 15, WHITE, True, mono=True, anchor="mm")


def dashed_line(draw, x0, y0, x1, y1, fill, width=2, dash=13, gap=9):
    length = math.hypot(x1 - x0, y1 - y0)
    if length == 0:
        return
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    pos = 0.0
    while pos < length:
        end = min(length, pos + dash)
        draw.line((x0 + ux * pos, y0 + uy * pos, x0 + ux * end, y0 + uy * end), fill=fill, width=width)
        pos += dash + gap


def draw_intro(local: float, duration: float) -> Image.Image:
    image, d = base_frame()
    header(d, "ACC LAB   /   STRESS TEST 01")
    pill(d, (82, 142, 416, 190), "A CONTROL QUESTION", CYAN)
    txt(d, (82, 250), "WHEN THE GAP", 98, WHITE, True)
    txt(d, (82, 364), "SHRINKS FAST", 98, WHITE, True)
    txt(d, (88, 518), "Can a small braking guard help", 38, MUTED)
    txt(d, (88, 569), "a tabular RL cruise controller?", 38, MUTED)
    # Dramatic but data-faithful road glyph; only longitudinal spacing moves.
    x0, y0, x1, y1 = 1205, 205, 1835, 816
    round_rect(d, (x0, y0, x1, y1), radius=30, fill=(14, 26, 43), outline=(37, 58, 80), width=2)
    txt(d, (1248, 246), "FOLLOWING GAP", 19, MUTED, True, mono=True)
    txt(d, (1790, 246), "MODEL VIEW", 17, FAINT, mono=True, anchor="ra")
    road_y = 506
    d.rounded_rectangle((1245, 390, 1795, 632), radius=20, fill=(24, 34, 48))
    d.line((1267, 406, 1774, 406), fill=(88, 108, 128), width=2)
    d.line((1267, 616, 1774, 616), fill=(88, 108, 128), width=2)
    for x in range(1275, 1760, 74):
        d.rounded_rectangle((x, road_y, x + 37, road_y + 6), radius=3, fill=(169, 185, 199))
    ego_x = 1300
    current_gap = 36 - 14 * min(1, max(0, local / 3.5))
    lead_x = ego_x + 104 + current_gap * 8.0
    draw_car(d, ego_x, 456, CYAN, "EGO", 110, 58)
    draw_car(d, lead_x, 456, AMBER, "LEAD", 110, 58)
    gx0, gx1 = ego_x + 112, lead_x - 6
    d.line((gx0, 566, gx1, 566), fill=WHITE, width=3)
    d.polygon([(gx0, 566), (gx0 + 13, 558), (gx0 + 13, 574)], fill=WHITE)
    d.polygon([(gx1, 566), (gx1 - 13, 558), (gx1 - 13, 574)], fill=WHITE)
    round_rect(d, (1457, 337, 1697, 394), radius=16, fill=(11, 19, 32), outline=(39, 57, 78), width=2)
    centered(d, 1577, 366, f"{current_gap:04.1f} m", 30, WHITE, True, mono=True)
    # A slim signal pulse illustrates the observed event, not a physical lane-change path.
    d.line((1280, 720, 1750, 720), fill=(49, 69, 91), width=3)
    event_x = 1280 + 470 * min(1, local / duration)
    d.line((event_x, 703, event_x, 737), fill=AMBER, width=4)
    txt(d, (1280, 750), "gap-step proxy", 18, AMBER, True)
    txt(d, (1750, 750), "time", 17, MUTED, mono=True, anchor="ra")
    round_rect(d, (82, 742, 1004, 852), radius=23, fill=(14, 27, 44), outline=(35, 52, 73), width=2)
    txt(d, (118, 768), "THE TEST", 18, CYAN, True, mono=True)
    txt(d, (118, 803), "Same cut-in event. Four controller references. 50 randomized seeds.", 25, WHITE)
    footer(d, "SIMULATION FILM  ·  10 Hz POINT-MASS MODEL  ·  NO ROAD-TEST CLAIM")
    return image


def draw_setup(local: float, duration: float) -> Image.Image:
    image, d = base_frame()
    header(d, "THE QUESTION, MADE TESTABLE")
    txt(d, (82, 143), "Small policy. Clear intervention.", 66, WHITE, True)
    txt(d, (88, 232), "The learned table adjusts a familiar controller instead of replacing it.", 30, MUTED)

    # Three-step method strip.
    cards = [
        (82, 348, 600, 680, VIOLET, "01", "LEARN", "Q-learning adds one of\nseven discrete acceleration\ncorrections to a CTG-PID base."),
        (660, 348, 1178, 680, CYAN, "02", "FILTER", "A braking-distance rule\ncan replace a proposed action\nwhen its check triggers."),
        (1156, 348, 1838, 680, AMBER, "03", "MEASURE", "Compare gap, short TTC and\njerk against classical PID\nand a predictive MPC reference."),
    ]
    for x0, y0, x1, y1, color, number, title, body in cards:
        round_rect(d, (x0, y0, x1, y1), radius=26, fill=PANEL, outline=(40, 59, 82), width=2)
        round_rect(d, (x0 + 30, y0 + 28, x0 + 103, y0 + 91), radius=19, fill=(23, 39, 58), outline=color, width=2)
        centered(d, x0 + 66, y0 + 59, number, 23, color, True, mono=True)
        txt(d, (x0 + 31, y0 + 127), title, 24, color, True, mono=True)
        y = y0 + 185
        for line in body.splitlines():
            txt(d, (x0 + 31, y), line, 24, WHITE)
            y += 42
    # Flow line and a small controller line-up anchor the method in control engineering.
    d.line((142, 757, 1778, 757), fill=(48, 66, 89), width=3)
    for x, color in ((142, VIOLET), (680, CYAN), (1204, AMBER), (1778, BLUE)):
        d.ellipse((x - 7, 750, x + 7, 764), fill=color)
    labels = ["CLASSICAL CTG-PID", "Q-LEARNING", "Q + GUARD", "MPC"]
    positions = [142, 680, 1204, 1778]
    for x, label in zip(positions, labels):
        centered(d, x, 805, label, 18, MUTED, True, mono=True)
    round_rect(d, (82, 866, 1838, 952), radius=21, fill=(13, 24, 40), outline=(36, 54, 75), width=2)
    txt(d, (114, 895), "FAIR COMPARISON", 18, CYAN, True, mono=True)
    txt(d, (380, 895), "Every controller gets the same initial state and event parameters for each seed.", 26, WHITE)
    footer(d, "METHOD DETAILS  ·  outputs/formal_50seed/experiment_manifest.json")
    return image


def load_trace(path: Path, scenario: str, controller: str) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["scenario"] == scenario and r["controller"] == controller]
    if not rows:
        raise ValueError(f"No {scenario!r} trace for {controller!r} in {path}")
    numeric = ["t", "gap", "desired_gap", "ego_speed", "lead_speed", "command",
               "acceleration", "jerk", "rss_margin", "intervention", "event_time_s"]
    for row in rows:
        for key in numeric:
            row[key] = float(row[key]) if row[key] not in ("", "nan", "NaN") else math.nan
    return rows


def draw_trace_plot(draw, box, rows: list[dict], idx: int, color):
    x0, y0, x1, y1 = box
    round_rect(draw, box, radius=15, fill=(11, 20, 34), outline=(43, 59, 79), width=2)
    plot = (x0 + 44, y0 + 25, x1 - 22, y1 - 36)
    px0, py0, px1, py1 = plot
    total = max(1, len(rows) - 1)
    ymax = 45.0
    for value in (0, 15, 30, 45):
        yy = py1 - value / ymax * (py1 - py0)
        draw.line((px0, yy, px1, yy), fill=(35, 52, 73), width=1)
        txt(draw, (x0 + 9, yy), str(value), 14, FAINT, mono=True, anchor="lm")
    event_time = rows[0]["event_time_s"]
    if math.isfinite(event_time):
        event_x = px0 + (px1 - px0) * event_time / max(rows[-1]["t"], 1)
        dashed_line(draw, event_x, py0 + 2, event_x, py1, AMBER, 2, 6, 6)
    def xy(i, value):
        x = px0 + (px1 - px0) * i / total
        y = py1 - max(0.0, min(ymax, value)) / ymax * (py1 - py0)
        return int(x), int(y)
    # Decimate only the drawn polyline, never the recorded metric or cursor position.
    stride = max(1, idx // 180)
    selected = list(range(0, idx + 1, stride))
    if selected[-1] != idx:
        selected.append(idx)
    measured = [xy(i, rows[i]["gap"]) for i in selected]
    target = [xy(i, rows[i]["desired_gap"]) for i in selected]
    if len(measured) > 1:
        draw.line(target, fill=(134, 151, 171), width=2)
        draw.line(measured, fill=color, width=4)
    cursor_x = px0 + (px1 - px0) * idx / total
    draw.line((int(cursor_x), py0, int(cursor_x), py1), fill=(220, 230, 239), width=2)
    cur_y = xy(idx, rows[idx]["gap"])[1]
    draw.ellipse((int(cursor_x) - 7, cur_y - 7, int(cursor_x) + 7, cur_y + 7), fill=color, outline=WHITE, width=2)


def draw_compare(local: float, duration: float, traces: dict[str, list[dict]], seed: int):
    image, d = base_frame()
    header(d, "THREE RESPONSES  /  ONE MATCHED EPISODE")
    txt(d, (82, 130), "Watch the same gap event unfold.", 54, WHITE, True)
    pill(d, (1324, 132, 1838, 181), f"SEED {seed:02d}  ·  CUT-IN HOLDOUT", AMBER, size=17)
    sim_time = min(39.9, max(0.0, local / duration * 39.9))
    txt(d, (84, 202), "Longitudinal proxy only  ·  instantaneous gap step  ·  no lane-change geometry", 20, MUTED)
    centered(d, 1685, 222, f"MODEL TIME  {sim_time:04.1f} s", 21, CYAN, True, mono=True)

    gap = 31
    outer = 80
    gutter = 29
    card_w = (W - outer * 2 - gutter * 2) // 3
    card_top, card_bottom = 274, 919
    for i, controller in enumerate(("Q-Learning", "Q+RSS", "MPC")):
        rows = traces[controller]
        color = TRACE_COLORS[controller]
        x0 = outer + i * (card_w + gutter)
        x1 = x0 + card_w
        idx = max(0, min(len(rows) - 1, int(sim_time / 0.1)))
        row = rows[idx]
        round_rect(d, (x0, card_top, x1, card_bottom), radius=27, fill=PANEL, outline=(46, 64, 88), width=2)
        d.rounded_rectangle((x0 + 2, card_top + 2, x1 - 2, card_top + 12), radius=5, fill=color)
        name, sub = DISPLAY_NAMES[controller]
        txt(d, (x0 + 28, card_top + 35), name, 25, color, True, mono=True)
        txt(d, (x0 + 28, card_top + 76), sub, 17, MUTED)

        # Road glyph: x-distance is proportional to the actual recorded gap.
        road_x0, road_x1 = x0 + 24, x1 - 24
        road_y0, road_y1 = card_top + 129, card_top + 305
        d.rounded_rectangle((road_x0, road_y0, road_x1, road_y1), radius=18, fill=(25, 35, 49))
        d.line((road_x0 + 12, road_y0 + 18, road_x1 - 12, road_y0 + 18), fill=(85, 103, 122), width=2)
        d.line((road_x0 + 12, road_y1 - 18, road_x1 - 12, road_y1 - 18), fill=(85, 103, 122), width=2)
        for rx in range(road_x0 + 16, road_x1 - 18, 62):
            d.rounded_rectangle((rx, road_y0 + 85, rx + 32, road_y0 + 90), radius=2, fill=(140, 155, 170))
        car_y = road_y0 + 48
        car_w, car_h = 92, 48
        ego_x = road_x0 + 37
        gap_px = max(23, min(205, float(row["gap"]) * 5.25))
        lead_x = ego_x + car_w + gap_px
        if lead_x + car_w > road_x1 - 6:
            lead_x = road_x1 - car_w - 6
        draw_car(d, ego_x, car_y, CYAN, "EGO", car_w, car_h)
        draw_car(d, lead_x, car_y, AMBER, "LEAD", car_w, car_h)
        gx0, gx1 = ego_x + car_w + 4, lead_x - 5
        if gx1 > gx0 + 8:
            d.line((gx0, car_y + 34, gx1, car_y + 34), fill=WHITE, width=2)
            d.line((gx0, car_y + 28, gx0, car_y + 40), fill=WHITE, width=2)
            d.line((gx1, car_y + 28, gx1, car_y + 40), fill=WHITE, width=2)
        round_rect(d, (x1 - 161, road_y0 + 16, x1 - 39, road_y0 + 57), radius=14,
                   fill=(10, 20, 32), outline=(52, 70, 91), width=1)
        centered(d, x1 - 100, road_y0 + 36, f"{row['gap']:04.1f} m", 20, WHITE, True, mono=True)

        # Live value strip and synchronized gap response chart.
        mid_y = card_top + 337
        txt(d, (x0 + 30, mid_y), "EGO", 14, FAINT, True, mono=True)
        txt(d, (x0 + 30, mid_y + 28), f"{row['ego_speed']:04.1f} m/s", 20, WHITE, True, mono=True)
        txt(d, (x0 + 218, mid_y), "LEAD", 14, FAINT, True, mono=True)
        txt(d, (x0 + 218, mid_y + 28), f"{row['lead_speed']:04.1f} m/s", 20, WHITE, True, mono=True)
        txt(d, (x1 - 30, mid_y), "APPLIED ACCEL", 14, FAINT, True, mono=True, anchor="ra")
        txt(d, (x1 - 30, mid_y + 28), f"{row['command']:+.1f} m/s²", 20, WHITE, True, mono=True, anchor="ra")
        plot_box = (x0 + 20, card_top + 414, x1 - 20, card_top + 601)
        draw_trace_plot(d, plot_box, rows, idx, color)
        txt(d, (x0 + 27, card_top + 615), "GAP  m", 14, FAINT, True, mono=True)
        d.line((x0 + 136, card_top + 628, x0 + 174, card_top + 628), fill=color, width=4)
        txt(d, (x0 + 182, card_top + 615), "measured", 15, MUTED)
        d.line((x0 + 300, card_top + 628, x0 + 338, card_top + 628), fill=(134, 151, 171), width=2)
        txt(d, (x0 + 347, card_top + 615), "desired", 15, MUTED)
        event_time = rows[0]["event_time_s"]
        event_state = "BEFORE GAP STEP" if sim_time < event_time else "AFTER GAP STEP"
        state_color = AMBER if sim_time >= event_time else MUTED
        txt(d, (x0 + card_w - 24, card_top + 615), event_state, 14, state_color, True, mono=True, anchor="ra")

    footer(d, "TRACE: SEED 17  ·  EVERY METHOD RECEIVES THE SAME SCRIPTED GAP EVENT")
    return image


def draw_evidence(local: float, duration: float, summary: dict[str, dict[str, float]]) -> Image.Image:
    image, d = base_frame()
    header(d, "50 RANDOMIZED, SEED-MATCHED CUT-IN EPISODES")
    txt(d, (82, 137), "The guard helps Q-learning.\nThe trade-off stays visible.", 59, WHITE, True)
    txt(d, (87, 292), "Mean episode minimum gap  ·  metres", 21, MUTED)
    # Group comparison bars from the 50-seed CSV summaries.
    rows = [
        ("CTG-PID", summary["CTG-PID"]["min_gap"], BLUE, "classical ACC baseline"),
        ("Q-LEARNING", summary["Q-Learning"]["min_gap"], VIOLET, "learned correction"),
        ("Q + GUARD", summary["Q+RSS"]["min_gap"], CYAN, "learned + filter"),
        ("MPC", summary["MPC"]["min_gap"], AMBER, "predictive reference"),
    ]
    bar_x, bar_w = 407, 620
    reveal = min(1.0, max(0.0, local / 3.0))
    for i, (name, value, color, note) in enumerate(rows):
        y = 367 + i * 128
        txt(d, (95, y + 5), name, 21, color, True, mono=True)
        txt(d, (95, y + 43), note, 16, MUTED)
        round_rect(d, (bar_x, y, bar_x + bar_w, y + 48), radius=15, fill=(24, 37, 55))
        actual_w = int(bar_w * value / 14.0 * reveal)
        if actual_w > 4:
            round_rect(d, (bar_x, y, bar_x + actual_w, y + 48), radius=15, fill=color)
        txt(d, (bar_x + actual_w + 17, y + 24), f"{value:.2f} m", 22, WHITE, True, mono=True, anchor="lm")

    # Guard effect and comfort cost.
    round_rect(d, (1114, 347, 1838, 879), radius=27, fill=(15, 28, 46), outline=(48, 67, 91), width=2)
    txt(d, (1154, 382), "Q + FILTER  vs  Q", 20, CYAN, True, mono=True)
    gap_gain = summary["Q+RSS"]["min_gap"] - summary["Q-Learning"]["min_gap"]
    txt(d, (1154, 440), f"+{gap_gain:.2f} m", 60, WHITE, True, mono=True)
    txt(d, (1158, 511), "mean episode minimum gap", 20, MUTED)
    d.line((1154, 568, 1798, 568), fill=(43, 61, 84), width=2)
    txt(d, (1154, 599), "closing samples with TTC < 2 s", 17, MUTED, True)
    txt(d, (1154, 635), f"{summary['Q-Learning']['ttc']:.2f}%  →  {summary['Q+RSS']['ttc']:.0f}%", 30, WHITE, True, mono=True)
    txt(d, (1154, 696), "mean absolute jerk", 18, MUTED, True)
    txt(d, (1154, 733), f"{summary['Q-Learning']['jerk']:.3f}  →  {summary['Q+RSS']['jerk']:.3f} m/s³", 26, AMBER, True, mono=True)
    txt(d, (1154, 802), f"MPC still has the largest mean minimum gap: {summary['MPC']['min_gap']:.2f} m.", 17, WHITE)
    footer(d, "50 EPISODES PER CONTROLLER  ·  NO COLLISIONS OBSERVED ≠ SAFETY GUARANTEE")
    return image


def draw_scope(local: float, duration: float) -> Image.Image:
    image, d = base_frame()
    header(d, "WHAT THE RESULT MEANS")
    txt(d, (82, 148), "A useful result.\nA narrow claim.", 82, WHITE, True)
    round_rect(d, (82, 399, 938, 868), radius=30, fill=PANEL, outline=(44, 64, 88), width=2)
    pill(d, (122, 439, 318, 484), "FINDING", CYAN, size=16)
    txt(d, (124, 535), "The braking guard", 31, WHITE, True)
    txt(d, (124, 581), "improved Q’s minimum-gap", 31, WHITE, True)
    txt(d, (124, 627), "and short-TTC metrics", 31, WHITE, True)
    txt(d, (124, 673), "in this modeled cut-in set.", 31, WHITE, True)
    txt(d, (124, 756), "MPC remained the strongest gap reference.", 22, AMBER, True)

    round_rect(d, (984, 148, 1838, 868), radius=30, fill=(14, 26, 43), outline=(44, 64, 88), width=2)
    txt(d, (1030, 197), "SCOPE & NEXT STEP", 20, CYAN, True, mono=True)
    notes = [
        ("01", "Cut-in is an instant longitudinal gap drop."),
        ("02", "No lane geometry, perception or sensor delay."),
        ("03", "No production ACC head-to-head was run."),
    ]
    y = 285
    for n, line in notes:
        round_rect(d, (1030, y, 1084, y + 48), radius=15, fill=(22, 40, 59), outline=(47, 69, 93), width=1)
        centered(d, 1057, y + 24, n, 16, AMBER, True, mono=True)
        txt(d, (1110, y + 24), line, 22, WHITE, anchor="lm")
        y += 102
    d.line((1030, 623, 1792, 623), fill=(42, 60, 82), width=2)
    txt(d, (1030, 658), "NEXT", 17, AMBER, True, mono=True)
    txt(d, (1110, 655), "Replay measured cut-in trajectories;", 22, WHITE)
    txt(d, (1110, 696), "then add lane and sensor models.", 22, WHITE)
    txt(d, (1030, 782), "Honda manual = feature context, not a matched benchmark.", 17, MUTED)
    footer(d, "REPRODUCIBLE RUN  ·  50 MATCHED SEEDS  ·  CPU-ONLY PROJECT")
    return image


SEGMENTS = [
    (4.5, draw_intro),
    (6.5, draw_setup),
]


def frame_at(time_s: float, traces: dict[str, list[dict]], seed: int,
             summary: dict[str, dict[str, float]], total: float) -> Image.Image:
    t = time_s
    starts = [0.0, 4.5, 11.0, 31.0, 41.0]
    durations = [4.5, 6.5, 20.0, 10.0, 7.0]
    renderers = [
        lambda p, dur: draw_intro(p, dur),
        lambda p, dur: draw_setup(p, dur),
        lambda p, dur: draw_compare(p, dur, traces, seed),
        lambda p, dur: draw_evidence(p, dur, summary),
        lambda p, dur: draw_scope(p, dur),
    ]
    for start, dur, render in zip(starts, durations, renderers):
        if start <= t < start + dur or (start + dur == total and t <= total):
            local = min(dur, max(0.0, t - start))
            image = render(local, dur)
            # Gentle fades at editorial boundaries; no abrupt cut to/from black.
            if start == 0.0:
                opacity = min(1.0, local / 0.45)
            elif start + dur == total:
                opacity = min(1.0, max(0.0, dur - local) / 0.40)
            else:
                opacity = 1.0
            if opacity < 1:
                image = Image.blend(Image.new("RGB", (W, H), INK), image, max(0.0, opacity))
            return image
    return draw_scope(durations[-1], durations[-1])


def read_summary(path: Path) -> dict[str, dict[str, float]]:
    summary = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["scenario"] == "cut_in":
                summary[row["controller"]] = {
                    "min_gap": float(row["min_gap_m_mean"]),
                    "ttc": float(row["ttc_below_2s_pct_mean"]),
                    "jerk": float(row["mean_abs_jerk_mps3_mean"]),
                    "collision": float(row["collision_mean"]),
                    "episodes": int(row["episodes"]),
                }
    expected = {"CTG-PID", "Q-Learning", "Q+RSS", "MPC"}
    if not expected.issubset(summary):
        raise ValueError(f"Missing cut_in summary rows: {expected - set(summary)}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", default="outputs/formal_50seed/representative_traces.csv")
    parser.add_argument("--summary", default="outputs/formal_50seed/scenario_summary.csv")
    parser.add_argument("--scenario", default="cut_in")
    parser.add_argument("--output", default="workspace/output/ACC_CutIn_Explainer.mp4")
    parser.add_argument("--fps", type=int, default=FPS)
    args = parser.parse_args()

    trace_path, summary_path, out = Path(args.trace), Path(args.summary), Path(args.output)
    traces = {name: load_trace(trace_path, args.scenario, name)
              for name in ("Q-Learning", "Q+RSS", "MPC")}
    for name, rows in traces.items():
        if not math.isclose(rows[-1]["t"], 39.9, abs_tol=0.11):
            raise ValueError(f"Expected a 40-second representative trace for {name}; found {rows[-1]['t']:.2f}s")
    summary = read_summary(summary_path)
    if any(row["episodes"] != 50 for row in summary.values()):
        raise ValueError("This film's current result card expects 50 cut-in episodes for every controller.")
    if any(row["collision"] != 0 for row in summary.values()):
        raise ValueError("Update the end-card collision caveat before rendering changed episode results.")
    q, guarded = summary["Q-Learning"], summary["Q+RSS"]
    if abs((guarded["min_gap"] - q["min_gap"]) - 4.35) > 0.03:
        raise ValueError("The video copy is calibrated for the current 50-seed cut-in result; update it before rendering changed summaries.")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to encode the MP4.")
    out.parent.mkdir(parents=True, exist_ok=True)
    total_s = sum((4.5, 6.5, 20.0, 10.0, 7.0))
    total_frames = round(total_s * args.fps)
    command = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-video_size", f"{W}x{H}",
        "-framerate", str(args.fps), "-i", "pipe:0", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out),
    ]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    try:
        for frame_idx in range(total_frames):
            t = frame_idx / args.fps
            frame = frame_at(t, traces, 17, summary, total_s)
            proc.stdin.write(frame.tobytes())
        proc.stdin.close()
        code = proc.wait()
        if code:
            raise subprocess.CalledProcessError(code, command)
    except Exception:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
        raise
    print(f"Wrote {out} · {total_s:.1f}s · {W}x{H} · {args.fps} fps · silent")


if __name__ == "__main__":
    main()
