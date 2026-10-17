"""Render a narrated, character-led explainer from the ACC project's real results.

The film uses vector lab characters and project CSV traces so its charts remain
faithful to the simulation. It requires Pillow, NumPy, macOS ``say``, and FFmpeg.
"""

from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


W, H, FPS = 1920, 1080, 24
INK = (8, 15, 28)
PANEL = (15, 27, 43)
PANEL_2 = (20, 35, 54)
WHITE = (242, 247, 252)
MUTED = (164, 180, 198)
FAINT = (104, 124, 147)
GRID = (37, 54, 75)
TEAL = (77, 220, 205)
VIOLET = (182, 151, 255)
AMBER = (255, 190, 105)
RED = (255, 112, 130)
BLUE = (107, 171, 255)
GREEN = (123, 226, 169)

FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_MONO = Path("/System/Library/Fonts/Menlo.ttc")
FONT_CACHE: dict[tuple[int, bool, bool], ImageFont.ImageFont] = {}


def font(size: int, bold: bool = False, mono: bool = False):
    key = (size, bold, mono)
    if key not in FONT_CACHE:
        path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REGULAR)
        try:
            FONT_CACHE[key] = ImageFont.truetype(str(path), size)
        except OSError:
            FONT_CACHE[key] = ImageFont.load_default()
    return FONT_CACHE[key]


def text(draw: ImageDraw.ImageDraw, xy, value: str, size: int, fill=WHITE,
         bold: bool = False, mono: bool = False, anchor=None):
    draw.text(xy, value, font=font(size, bold, mono), fill=fill, anchor=anchor)


def center(draw: ImageDraw.ImageDraw, x: int, y: int, value: str, size: int,
           fill=WHITE, bold: bool = False, mono: bool = False):
    text(draw, (x, y), value, size, fill, bold, mono, anchor="mm")


def box(draw, bounds, radius=22, fill=PANEL, outline=None, width=1):
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def pill(draw, x: int, y: int, label: str, color=TEAL, width: int | None = None):
    width = width or max(176, len(label) * 13 + 40)
    box(draw, (x, y, x + width, y + 46), 21, (18, 37, 53), tuple(min(255, c + 15) for c in color), 2)
    text(draw, (x + 20, y + 23), label.upper(), 17, color, True, True, anchor="lm")


def make_background() -> Image.Image:
    yy, xx = np.mgrid[0:H, 0:W]
    p = yy.astype(np.float32) / (H - 1)
    edge = xx.astype(np.float32) / (W - 1)
    top = np.array([12, 25, 42], dtype=np.float32)
    bottom = np.array([7, 13, 25], dtype=np.float32)
    base = top[None, None, :] * (1.0 - p[:, :, None]) + bottom[None, None, :] * p[:, :, None]
    glow = np.exp(-(((edge - 0.72) / 0.34) ** 2 + ((p - 0.28) / 0.42) ** 2))[:, :, None]
    cool = np.array([2.0, 9.0, 14.0], dtype=np.float32)
    base += glow * cool[None, None, :]
    image = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(image)
    for x in range(48, W, 96):
        d.line((x, 0, x, H), fill=(13, 25, 40), width=1)
    for y in range(48, H, 96):
        d.line((0, y, W, y), fill=(13, 25, 40), width=1)
    for x in range(44, W, 48):
        for y in range(44, H, 48):
            if (x // 48 + y // 48) % 5 == 0:
                d.ellipse((x - 1, y - 1, x + 1, y + 1), fill=(34, 53, 73))
    return image


BG = make_background()


def new_frame() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = BG.copy()
    return image, ImageDraw.Draw(image)


def header(draw, label: str, section: str):
    text(draw, (78, 48), label.upper(), 18, TEAL, True, True)
    text(draw, (W - 80, 50), section.upper(), 16, MUTED, False, True, anchor="ra")
    draw.line((78, 88, W - 78, 88), fill=GRID, width=2)


def footer(draw, left: str, progress: float):
    draw.line((78, 1034, W - 78, 1034), fill=GRID, width=2)
    text(draw, (80, 1051), left, 16, MUTED, False, True, anchor="lm")
    draw.rounded_rectangle((W - 450, 1046, W - 80, 1056), radius=5, fill=(32, 48, 68))
    draw.rounded_rectangle((W - 450, 1046, W - 450 + round(370 * progress), 1056), radius=5, fill=TEAL)


def car(draw, x: float, y: float, color, label: str, scale=1.0):
    w, h = int(156 * scale), int(80 * scale)
    x, y = int(x), int(y)
    draw.rounded_rectangle((x, y + int(25 * scale), x + w, y + h),
                           radius=int(22 * scale), fill=color, outline=(222, 236, 247), width=max(1, int(2 * scale)))
    draw.polygon([(x + 19 * scale, y + 28 * scale), (x + 43 * scale, y + 6 * scale),
                  (x + w - 37 * scale, y + 6 * scale), (x + w - 12 * scale, y + 29 * scale)], fill=color)
    draw.rounded_rectangle((x + 52 * scale, y + 12 * scale, x + w - 46 * scale, y + 28 * scale),
                           radius=max(2, int(5 * scale)), fill=(168, 194, 211), outline=(221, 233, 241), width=1)
    for wheel_x in (x + 24 * scale, x + w - 53 * scale):
        r = 16 * scale
        draw.ellipse((wheel_x, y + h - r, wheel_x + 2 * r, y + h + r), fill=(5, 10, 18), outline=(118, 137, 158), width=max(1, int(2 * scale)))
        draw.ellipse((wheel_x + 7 * scale, y + h - r + 7 * scale, wheel_x + 25 * scale, y + h + 9 * scale), fill=(105, 123, 145))
    draw.ellipse((x + w - 10 * scale, y + 43 * scale, x + w - 2 * scale, y + 53 * scale), fill=(255, 239, 192))
    draw.ellipse((x + 2 * scale, y + 43 * scale, x + 10 * scale, y + 53 * scale), fill=RED)
    text(draw, (x + w / 2, y + h + 31 * scale), label.upper(), max(12, int(13 * scale)), WHITE, True, True, anchor="mm")


def person(draw, cx: float, top: float, scale=1.0, who="mira", pose="listen", phase=0.0):
    """Stable flat-illustration character. The pose changes; identity colors and shape do not."""
    s = scale
    cx, top = float(cx), float(top)
    is_mira = who.lower() == "mira"
    skin = (192, 126, 89) if is_mira else (139, 83, 62)
    hair = (21, 22, 31) if is_mira else (19, 21, 32)
    shirt = (27, 139, 143) if is_mira else (45, 61, 112)
    accent = AMBER if is_mira else (244, 169, 71)
    bob = 1.7 * math.sin(phase * 1.7 + (0 if is_mira else 1.2))
    head_cx = cx + (0 if is_mira else 6 * s)
    head_top = top + 34 * s + bob
    head_w, head_h = 120 * s, 156 * s

    # Soft ground shadow keeps each figure seated in the illustration.
    draw.ellipse((cx - 132 * s, top + 485 * s, cx + 138 * s, top + 520 * s), fill=(7, 13, 23))
    # Torso and neck.
    draw.rounded_rectangle((cx - 30 * s, top + 184 * s, cx + 31 * s, top + 242 * s), radius=11 * s, fill=skin)
    torso = [(cx - 84 * s, top + 226 * s), (cx - 48 * s, top + 210 * s),
             (cx + 48 * s, top + 210 * s), (cx + 87 * s, top + 245 * s),
             (cx + 102 * s, top + 436 * s), (cx - 103 * s, top + 436 * s)]
    draw.polygon(torso, fill=shirt)
    draw.line((cx - 78 * s, top + 430 * s, cx - 81 * s, top + 499 * s), fill=(31, 38, 55), width=max(2, int(38 * s)))
    draw.line((cx + 77 * s, top + 430 * s, cx + 81 * s, top + 499 * s), fill=(31, 38, 55), width=max(2, int(38 * s)))
    # Arms carry simple, readable business rather than theatrical gestures.
    shoulder_y = top + 255 * s
    if pose in ("point", "mark"):
        elbow_a = (cx - 115 * s, top + 322 * s)
        hand_a = (cx - 52 * s, top + 291 * s)
        shoulder_b = (cx + 70 * s, shoulder_y)
        elbow_b = (cx + 127 * s, top + 333 * s)
        hand_b = (cx + 153 * s, top + 386 * s)
    elif pose == "open":
        elbow_a, hand_a = (cx - 135 * s, top + 312 * s), (cx - 182 * s, top + 295 * s)
        elbow_b, hand_b = (cx + 135 * s, top + 313 * s), (cx + 181 * s, top + 292 * s)
        shoulder_b = (cx + 70 * s, shoulder_y)
    else:
        elbow_a, hand_a = (cx - 129 * s, top + 341 * s), (cx - 110 * s, top + 402 * s)
        shoulder_b = (cx + 70 * s, shoulder_y)
        elbow_b, hand_b = (cx + 124 * s, top + 328 * s), (cx + 133 * s, top + 382 * s)
    shoulder_a = (cx - 70 * s, shoulder_y)
    for shoulder, elbow, hand in ((shoulder_a, elbow_a, hand_a), (shoulder_b, elbow_b, hand_b)):
        dwidth = max(2, int(33 * s))
        draw.line((shoulder, elbow), fill=shirt, width=dwidth)
        draw.line((elbow, hand), fill=shirt, width=dwidth)
        draw.ellipse((hand[0] - 12 * s, hand[1] - 12 * s, hand[0] + 12 * s, hand[1] + 12 * s), fill=skin)
    # Head, hair and facial markers.
    draw.ellipse((head_cx - head_w / 2, head_top, head_cx + head_w / 2, head_top + head_h), fill=skin)
    draw.pieslice((head_cx - head_w / 2 - 9 * s, head_top - 13 * s,
                   head_cx + head_w / 2 + 9 * s, head_top + 110 * s), 180, 360, fill=hair)
    if is_mira:
        draw.rounded_rectangle((head_cx - head_w / 2 - 7 * s, head_top + 37 * s,
                                head_cx - head_w / 2 + 21 * s, head_top + 176 * s), radius=18 * s, fill=hair)
        draw.rounded_rectangle((head_cx + head_w / 2 - 18 * s, head_top + 44 * s,
                                head_cx + head_w / 2 + 10 * s, head_top + 168 * s), radius=18 * s, fill=hair)
        draw.polygon([(head_cx - 60 * s, head_top + 40 * s), (head_cx - 7 * s, head_top - 5 * s),
                      (head_cx + 56 * s, head_top + 20 * s), (head_cx + 44 * s, head_top + 50 * s)], fill=hair)
    else:
        for dx, dy, rr in [(-46, 7, 19), (-17, -4, 18), (15, -6, 18), (45, 8, 18), (-53, 31, 14), (51, 31, 14)]:
            draw.ellipse((head_cx + (dx - rr) * s, head_top + (dy - rr) * s,
                          head_cx + (dx + rr) * s, head_top + (dy + rr) * s), fill=hair)
    eye_y = head_top + 79 * s
    for ex in (-23, 22):
        draw.ellipse((head_cx + (ex - 5) * s, eye_y, head_cx + (ex + 5) * s, eye_y + 8 * s), fill=(17, 22, 31))
        draw.line((head_cx + (ex - 9) * s, eye_y - 8 * s, head_cx + (ex + 8) * s, eye_y - 11 * s), fill=hair, width=max(1, int(3 * s)))
    draw.line((head_cx + 1 * s, eye_y + 10 * s, head_cx - 3 * s, eye_y + 29 * s), fill=(118, 68, 53), width=max(1, int(2 * s)))
    draw.arc((head_cx - 18 * s, eye_y + 29 * s, head_cx + 17 * s, eye_y + 50 * s), 5, 170, fill=(103, 51, 47), width=max(1, int(3 * s)))
    if not is_mira:
        # Dev's locked round-rectangle glasses are his distinguishing prop.
        for ex in (-23, 22):
            draw.rounded_rectangle((head_cx + (ex - 13) * s, eye_y - 9 * s,
                                    head_cx + (ex + 13) * s, eye_y + 17 * s), radius=5 * s,
                                   outline=(32, 39, 54), width=max(1, int(3 * s)))
        draw.line((head_cx - 10 * s, eye_y + 2 * s, head_cx + 9 * s, eye_y + 2 * s), fill=(32, 39, 54), width=max(1, int(2 * s)))
    # Repeating clothing accents make the two silhouettes distinct.
    if is_mira:
        draw.line((cx + 5 * s, top + 239 * s, cx + 20 * s, top + 380 * s), fill=accent, width=max(2, int(5 * s)))
        draw.ellipse((cx + 8 * s, top + 309 * s, cx + 20 * s, top + 321 * s), fill=accent)
    else:
        draw.line((cx - 78 * s, top + 280 * s, cx - 58 * s, top + 285 * s), fill=accent, width=max(2, int(7 * s)))
        draw.rounded_rectangle((cx - 68 * s, top + 328 * s, cx - 18 * s, top + 374 * s), radius=5 * s,
                               outline=(136, 154, 189), width=max(1, int(2 * s)))


def write_character_references(folder: Path):
    folder.mkdir(parents=True, exist_ok=True)
    for who, name, tint in (("mira", "Mira", (31, 50, 69)), ("dev", "Dev", (36, 50, 74))):
        im = Image.new("RGB", (1024, 1024), (219, 225, 228))
        d = ImageDraw.Draw(im)
        d.ellipse((165, 805, 860, 930), fill=(195, 202, 206))
        # A light neutral studio background and one person only make the face lock useful.
        person(d, 515, 162, 1.36, who, "listen", 0.1)
        im.save(folder / f"{name}_Character_Reference.png", optimize=True)
    lab = Image.new("RGB", (1600, 900), (12, 25, 42))
    d = ImageDraw.Draw(lab)
    box(d, (62, 56, 1538, 844), 38, (15, 31, 49), (58, 82, 105), 3)
    d.rectangle((94, 91, 1506, 756), fill=(18, 35, 54))
    # Flat matte monitor panels in a single university engineering lab.
    for x, y, w, h in ((812, 194, 570, 318), (180, 223, 445, 280)):
        box(d, (x, y, x + w, y + h), 19, (8, 18, 31), (50, 73, 97), 2)
        d.rounded_rectangle((x + 20, y + 21, x + w - 20, y + h - 37), radius=11, fill=(17, 39, 56))
    d.rectangle((94, 680, 1506, 755), fill=(31, 43, 55))
    d.line((94, 681, 1506, 681), fill=(83, 105, 125), width=3)
    lab.save(folder / "ACC_Lab_Environment_Reference.png", optimize=True)


NARRATION = [
    "In their automotive controls lab, Mira asks a focused question: can a small reinforcement-learning correction help adaptive cruise control respond to a sudden cut-in? Dev adds one condition: measure comfort as well as spacing.",
    "Adaptive cruise follows a target time gap. A cut-in suddenly reduces available distance, putting gap control and smooth braking under pressure. Here, the cut-in is represented as an instantaneous one-dimensional gap step.",
    "The base is a constant-time-gap PID controller. Tabular Q-learning adds one of seven discrete acceleration corrections. A simplified, RSS-inspired braking guard checks the proposed command against a stopping-margin rule, then substitutes a passing command when needed.",
    "The table is trained for six thousand episodes on steady, wave and moderate-braking profiles. Then four controllers are compared across five scenario families and 50 matched seeds each. Cut-in and emergency braking are held out.",
    "Without the guard, Q-learning averaged a 7.00 metre episode minimum gap across 50 cut-in seeds. The mean share of closing samples with time-to-collision under two seconds was 2.04 percent.",
    "With the guard, mean minimum gap increased to 11.35 metres, and that low-TTC share fell to zero. Mean absolute jerk rose from 0.96 to 1.22 metres per second cubed. MPC reached 13.11 metres, zero low-TTC share, and lower jerk at 0.63.",
    "These runs recorded no collisions across the four controllers; that is not a safety guarantee. The simulation has one-dimensional point-mass motion, a synthetic gap step, and no lane-change or perception model. The team's next step is measured cut-in replay. This project asks how a small learned correction and an explicit braking check trade margin against comfort before any road claim.",
]

SCENE_TITLES = [
    ("A CAR-FOLLOWING QUESTION", "Mira sets the question; Dev asks for a fair test."),
    ("WHEN THE GAP SHRINKS", "A cut-in stresses distance and comfort at once."),
    ("A SMALL LEARNER, BOUNDED ACTION", "Q-learning adds a residual; a simple guard checks it."),
    ("TRAIN, THEN HOLD OUT", "6,000 training episodes. 1,000 matched evaluation episodes."),
    ("SAME EVENT. SAME SEEDS.", "Without guard vs. with guard, measured over 50 seeds."),
    ("HELPFUL, WITH A COMFORT COST", "The guard helps gap metrics; MPC remains the reference."),
    ("WHAT THE SIMULATION CAN CLAIM", "A useful controls study, not a road-safety proof."),
]


@dataclass
class SceneTiming:
    start: float
    speech: float
    end: float


def run(cmd: list[str]):
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def probe_duration(path: Path) -> float:
    output = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path),
    ], text=True)
    return float(output.strip())


def make_voice_segments(temp_dir: Path, voice: str, rate: int, ffmpeg: str) -> tuple[list[Path], list[float]]:
    say = shutil.which("say")
    if not say:
        raise RuntimeError("macOS 'say' is required for narration. Run on this Mac or use --no-voiceover.")
    raw_files, durations = [], []
    for index, paragraph in enumerate(NARRATION, start=1):
        aiff = temp_dir / f"voice_{index:02d}.aiff"
        raw = temp_dir / f"voice_{index:02d}.s16le"
        subprocess.run([say, "-v", voice, "-r", str(rate), "-o", str(aiff), "--", paragraph], check=True)
        run([ffmpeg, "-y", "-hide_banner", "-loglevel", "error", "-i", str(aiff),
             "-ac", "1", "-ar", "48000", "-f", "s16le", str(raw)])
        raw_files.append(raw)
        durations.append(raw.stat().st_size / 2 / 48000)
    return raw_files, durations


def load_csv(path: Path, scenario: str, controller: str) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["scenario"] == scenario and r["controller"] == controller]
    if not rows:
        raise ValueError(f"No {scenario} trace for {controller} in {path}")
    for row in rows:
        for key in ("t", "gap", "desired_gap", "event_time_s"):
            row[key] = float(row[key]) if row[key] not in ("", "nan", "NaN") else math.nan
    return rows


def load_summary(path: Path) -> dict[str, dict[str, float]]:
    summary = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["scenario"] == "cut_in":
                summary[row["controller"]] = {
                    "episodes": int(row["episodes"]),
                    "min_gap": float(row["min_gap_m_mean"]),
                    "ttc": float(row["ttc_below_2s_pct_mean"]),
                    "jerk": float(row["mean_abs_jerk_mps3_mean"]),
                    "collision": float(row["collision_mean"]),
                }
    required = {"CTG-PID", "MPC", "Q-Learning", "Q+RSS"}
    if not required.issubset(summary):
        raise ValueError(f"Missing cut-in summary controllers: {required - set(summary)}")
    if any(summary[k]["episodes"] != 50 for k in required):
        raise ValueError("This story's result cards expect 50 matched cut-in seeds per controller.")
    return summary


def arrow(draw, start, end, color=TEAL, width=5):
    draw.line((*start, *end), fill=color, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = 16
    points = [end,
              (end[0] - length * math.cos(angle - 0.45), end[1] - length * math.sin(angle - 0.45)),
              (end[0] - length * math.cos(angle + 0.45), end[1] - length * math.sin(angle + 0.45))]
    draw.polygon(points, fill=color)


def draw_gap_plot(draw, bounds, rows: list[dict], local: float, duration: float, color, label: str):
    x0, y0, x1, y1 = bounds
    box(draw, bounds, 18, (8, 18, 31), (46, 65, 87), 2)
    text(draw, (x0 + 22, y0 + 18), label, 17, color, True, True)
    px0, py0, px1, py1 = x0 + 55, y0 + 67, x1 - 22, y1 - 47
    total_time = max(rows[-1]["t"], 1.0)
    max_gap = 45.0
    for val in (0, 15, 30, 45):
        yy = py1 - val / max_gap * (py1 - py0)
        draw.line((px0, yy, px1, yy), fill=(34, 51, 71), width=1)
        text(draw, (x0 + 17, yy), str(val), 12, FAINT, False, True, anchor="lm")
    event = rows[0]["event_time_s"]
    if math.isfinite(event):
        ex = px0 + (px1 - px0) * event / total_time
        for yy in range(py0, py1, 14):
            draw.line((ex, yy, ex, min(py1, yy + 7)), fill=AMBER, width=2)
    upto = max(2, min(len(rows), int((local / max(duration, 0.1)) * (len(rows) - 1)) + 1))
    points = []
    for row in rows[:upto]:
        xx = px0 + (px1 - px0) * row["t"] / total_time
        yy = py1 - max(0, min(max_gap, row["gap"])) / max_gap * (py1 - py0)
        points.append((int(xx), int(yy)))
    if len(points) > 1:
        draw.line(points, fill=color, width=4, joint="curve")
    if points:
        px, py = points[-1]
        draw.ellipse((px - 6, py - 6, px + 6, py + 6), fill=WHITE, outline=color, width=3)
    text(draw, (px0, y1 - 25), "0 s", 13, FAINT, False, True)
    text(draw, (px1, y1 - 25), "40 s", 13, FAINT, False, True, anchor="ra")


def draw_lab_scene(draw, t: float):
    # Matte screens, desk, and fixed lab geometry.
    box(draw, (87, 136, 1832, 825), 29, (12, 27, 44), (52, 76, 99), 2)
    box(draw, (942, 202, 1767, 605), 19, (5, 12, 22), (62, 88, 112), 2)
    draw.rounded_rectangle((970, 230, 1738, 568), radius=10, fill=(16, 35, 52))
    draw.rectangle((87, 739, 1832, 825), fill=(31, 43, 56))
    draw.line((87, 739, 1832, 739), fill=(85, 105, 125), width=3)
    draw.rectangle((1040, 605, 1667, 650), fill=(27, 36, 50))
    draw.rectangle((1085, 650, 1124, 739), fill=(27, 36, 50))
    draw.rectangle((1580, 650, 1619, 739), fill=(27, 36, 50))
    person(draw, 376, 331, 0.83, "mira", "point", t)
    person(draw, 701, 331, 0.83, "dev", "listen", t)
    text(draw, (279, 785), "MIRA", 16, TEAL, True, True, anchor="mm")
    text(draw, (703, 785), "DEV", 16, AMBER, True, True, anchor="mm")


def draw_scene_1(local, duration):
    image, d = new_frame()
    header(d, "AUTOMOTIVE CONTROL STUDY", "01  /  THE QUESTION")
    draw_lab_scene(d, local)
    # Schematic display is authored here rather than generated by the video model.
    text(d, (1008, 260), "ACC SIMULATION", 18, MUTED, True, True)
    car(d, 1110, 403, TEAL, "EGO", 0.87)
    gap = max(66, 328 - 120 * (local / max(duration, 0.01)))
    car(d, 1110 + 142 + gap, 403, AMBER, "LEAD", 0.87)
    d.line((1260, 526, 1260 + gap, 526), fill=WHITE, width=3)
    d.polygon([(1260, 526), (1270, 520), (1270, 532)], fill=WHITE)
    d.polygon([(1260 + gap, 526), (1250 + gap, 520), (1250 + gap, 532)], fill=WHITE)
    box(d, (1300, 301, 1540, 350), 15, (7, 18, 29), (57, 83, 107), 2)
    center(d, 1420, 325, "GAP CHANGES", 19, WHITE, True, True)
    pill(d, 1010, 565, "ILLUSTRATIVE MODEL VIEW", AMBER, 290)
    box(d, (1054, 671, 1661, 722), 13, (11, 22, 36), (39, 58, 78), 1)
    center(d, 1357, 696, "Can a small RL correction help?", 25, WHITE, True)
    text(d, (79, 139), "A SMALL POLICY. A REAL CONTROL QUESTION.", 16, TEAL, True, True)
    footer(d, "STORY  /  MIRA + DEV  /  MEASURE BEFORE MAKING A CLAIM", (local / duration) * (1 / 7))
    return image


def draw_scene_2(local, duration):
    image, d = new_frame()
    header(d, "WHY ADAPTIVE CRUISE CONTROL?", "02  /  THE STRESS CASE")
    text(d, (84, 131), "A following gap can change in an instant.", 49, WHITE, True)
    text(d, (89, 198), "The experiment compresses a cut-in into a one-dimensional gap-step proxy.", 24, MUTED)
    # Road glyph is a longitudinal state diagram, not a lane-change animation.
    box(d, (88, 295, 1325, 720), 27, (13, 25, 41), (43, 64, 86), 2)
    text(d, (122, 330), "SIMULATED FOLLOWING PAIR", 18, MUTED, True, True)
    road_y = 505
    d.rounded_rectangle((135, 443, 1278, 596), radius=18, fill=(27, 38, 52))
    d.line((155, 455, 1257, 455), fill=(86, 108, 129), width=2)
    d.line((155, 584, 1257, 584), fill=(86, 108, 129), width=2)
    for xx in range(175, 1220, 87):
        d.rounded_rectangle((xx, road_y, xx + 44, road_y + 6), radius=3, fill=(160, 178, 194))
    phase = max(0.0, min(1.0, (local - 2.0) / max(1.0, duration - 4.0)))
    spacing = int(408 - 205 * phase)
    car(d, 265, 468, TEAL, "EGO", 0.92)
    car(d, 265 + 150 + spacing, 468, AMBER, "LEAD", 0.92)
    # A vertical event marker means a measured distance step, not lateral path dynamics.
    event_x = 274 + 150 + spacing
    d.line((event_x, 383, event_x, 427), fill=RED, width=5)
    d.polygon([(event_x - 10, 421), (event_x + 10, 421), (event_x, 437)], fill=RED)
    center(d, 772, 390, "INSTANTANEOUS GAP STEP", 20, RED, True, True)
    d.line((431, 637, 431 + spacing, 637), fill=WHITE, width=3)
    d.polygon([(431, 637), (444, 629), (444, 645)], fill=WHITE)
    d.polygon([(431 + spacing, 637), (418 + spacing, 629), (418 + spacing, 645)], fill=WHITE)
    center(d, 714, 675, "Distance + relative speed drive the response", 23, WHITE)
    # Desired-gap rule.
    box(d, (1372, 295, 1834, 720), 27, (17, 31, 48), (47, 69, 92), 2)
    text(d, (1410, 338), "TARGET GAP", 18, TEAL, True, True)
    center(d, 1603, 444, "d* = 5 m + 1.3 v", 36, WHITE, True, True)
    center(d, 1603, 503, "v in metres per second", 18, MUTED)
    d.line((1434, 552, 1772, 552), fill=GRID, width=2)
    center(d, 1603, 603, "Balance spacing\nwith smooth control", 25, WHITE, True)
    pill(d, 1422, 655, "ONE-DIMENSIONAL PROXY", AMBER, 365)
    person(d, 150, 790, 0.38, "mira", "mark", local)
    person(d, 258, 790, 0.38, "dev", "listen", local)
    text(d, (346, 831), "Mira tracks the gap. Dev watches the response.", 19, MUTED)
    footer(d, "SIMULATED CUT-IN = GAP STEP; LANE-CHANGE PHYSICS ARE NOT MODELED", (1 + local / duration) / 7)
    return image


def draw_scene_3(local, duration):
    image, d = new_frame()
    header(d, "CONTROLLER DESIGN", "03  /  HOW IT WORKS")
    text(d, (84, 134), "Keep the familiar controller. Learn a small correction.", 46, WHITE, True)
    text(d, (89, 200), "The guard checks the proposed action before the simulated vehicle receives it.", 24, MUTED)
    # Input cards.
    input_items = [("GAP ERROR", TEAL), ("CLOSING SPEED", BLUE), ("EGO SPEED", AMBER), ("ACCELERATION", VIOLET)]
    for i, (label, color) in enumerate(input_items):
        x0, y0 = 92 + i * 281, 302
        box(d, (x0, y0, x0 + 240, y0 + 72), 18, PANEL, (45, 66, 89), 2)
        center(d, x0 + 120, y0 + 36, label, 17, color, True, True)
        arrow(d, (x0 + 120, y0 + 77), (x0 + 120, 424), color, 3)
    # Main control pipeline.
    blocks = [
        ("CTG-PID", "classical base", BLUE),
        ("+ Q TABLE", "one of 7 residuals", VIOLET),
        ("PROPOSED\nCOMMAND", "bounded acceleration", AMBER),
        ("BRAKING\nGUARD", "margin check", TEAL),
        ("VEHICLE\nMODEL", "actuator + motion", GREEN),
    ]
    xs = [88, 432, 776, 1120, 1464]
    for x0, (label, desc, color) in zip(xs, blocks):
        box(d, (x0, 461, x0 + 282, 650), 23, (15, 29, 46), (53, 76, 100), 2)
        center(d, x0 + 141, 521, label, 25, color, True, True)
        center(d, x0 + 141, 595, desc, 17, MUTED)
    for x0 in xs[:-1]:
        arrow(d, (x0 + 288, 553), (x0 + 330, 553), TEAL, 4)
    # Q residual enters between classical base and proposed command.
    arrow(d, (558, 674), (558, 656), VIOLET, 3)
    box(d, (400, 680, 710, 733), 13, (20, 35, 54), (102, 81, 148), 2)
    center(d, 555, 707, "Δa ∈ 7 discrete choices", 17, VIOLET, True, True)
    box(d, (1091, 678, 1810, 755), 14, (14, 31, 46), (43, 75, 91), 2)
    text(d, (1121, 704), "SIMPLIFIED RSS-INSPIRED CHECK", 17, TEAL, True, True)
    text(d, (1121, 731), "A course-project filter; not formal RSS or a safety proof.", 18, MUTED)
    # Characters stay in the lower quiet band.
    person(d, 314, 778, 0.36, "mira", "mark", local)
    person(d, 420, 778, 0.36, "dev", "point", local)
    text(d, (490, 830), "Small, inspectable, CPU-friendly control stack", 19, MUTED)
    footer(d, "TABULAR Q-LEARNING  /  7 ACTION CORRECTIONS  /  FIRST-ORDER VEHICLE MODEL", (2 + local / duration) / 7)
    return image


def draw_scene_4(local, duration):
    image, d = new_frame()
    header(d, "EXPERIMENT PLAN", "04  /  TRAIN AND TEST")
    text(d, (84, 135), "Training and evaluation use different events.", 48, WHITE, True)
    text(d, (89, 201), "The held-out cut-ins test generalization beyond the learned profiles.", 24, MUTED)
    # Training half.
    box(d, (86, 294, 906, 793), 25, (14, 27, 44), (47, 69, 92), 2)
    pill(d, 120, 326, "TRAIN", VIOLET, 155)
    text(d, (122, 398), "6,000", 75, WHITE, True, True)
    text(d, (401, 432), "episodes", 24, MUTED)
    train_profiles = [("STEADY", BLUE), ("WAVE", TEAL), ("MODERATE BRAKE", AMBER)]
    for i, (name, color) in enumerate(train_profiles):
        y = 531 + 62 * i
        box(d, (124, y, 760, y + 42), 12, (8, 18, 31), (37, 56, 78), 1)
        d.rounded_rectangle((131, y + 6, 131 + int(520 * (0.55 + 0.12 * math.sin(local * 2 + i))), y + 36), radius=7, fill=color)
        text(d, (790, y + 21), name, 16, color, True, True, anchor="lm")
    text(d, (124, 751), "Tabular Q-learning  ·  seed 17  ·  epsilon 1.0 → 0.05", 16, MUTED, False, True)
    # Test half.
    box(d, (1014, 294, 1835, 793), 25, (14, 27, 44), (47, 69, 92), 2)
    pill(d, 1048, 326, "HELD-OUT EVALUATION", TEAL, 315)
    text(d, (1050, 398), "1,000", 75, WHITE, True, True)
    text(d, (1328, 432), "matched runs", 24, MUTED)
    test_cases = [("CUT-IN", RED), ("EMERGENCY BRAKE", AMBER)]
    for i, (name, color) in enumerate(test_cases):
        y = 520 + i * 87
        box(d, (1050, y, 1774, y + 63), 16, (8, 18, 31), (39, 57, 79), 1)
        for j in range(10):
            for k in range(2):
                xx, yy = 1072 + j * 28, y + 18 + k * 19
                d.ellipse((xx, yy, xx + 10, yy + 10), fill=color if (j + k) % 3 else (57, 72, 92))
        text(d, (1390, y + 32), name, 16, color, True, True, anchor="lm")
        text(d, (1708, y + 32), "50 seeds", 15, MUTED, False, True, anchor="rm")
    text(d, (1051, 751), "4 controllers  ×  5 scenario families  ×  50 seeds", 17, MUTED, False, True)
    # Shared-seed ribbon.
    box(d, (86, 838, 1835, 917), 19, (11, 25, 40), (47, 73, 91), 2)
    center(d, 960, 877, "For each seed, controllers receive the same initial state and event parameters.", 25, WHITE, True)
    footer(d, "50 CUT-IN EPISODES PER CONTROLLER  /  50 EMERGENCY EPISODES PER CONTROLLER", (3 + local / duration) / 7)
    return image


def draw_scene_5(local, duration, traces, summary):
    image, d = new_frame()
    header(d, "WITHOUT GUARD  /  WITH GUARD", "05  /  THE DIRECT COMPARISON")
    text(d, (84, 133), "Same event. Same seed. Different action filter.", 46, WHITE, True)
    text(d, (89, 197), "Top panels follow representative seed 17; cards below summarize 50 matched cut-in runs.", 22, MUTED)
    phase = local / max(duration, 0.01)
    q, guarded = summary["Q-Learning"], summary["Q+RSS"]
    gap = 4.35 * max(0.0, min(1.0, (phase - 0.25) / 0.65))
    # Split screen with actual CSV gap traces.
    box(d, (84, 278, 932, 728), 24, (12, 25, 41), (68, 59, 96), 2)
    box(d, (988, 278, 1836, 728), 24, (12, 29, 44), (47, 88, 91), 2)
    pill(d, 119, 305, "WITHOUT GUARD", VIOLET, 254)
    pill(d, 1024, 305, "WITH SIMPLIFIED GUARD", TEAL, 340)
    draw_gap_plot(d, (113, 370, 904, 659), traces["Q-Learning"], local, duration, VIOLET, "Q-LEARNING  /  SEED 17")
    draw_gap_plot(d, (1017, 370, 1808, 659), traces["Q+RSS"], local, duration, TEAL, "Q + GUARD  /  SEED 17")
    # Aggregate results remain the primary claim; the representative traces are illustrative.
    box(d, (111, 680, 905, 783), 17, (11, 22, 36), (69, 59, 98), 2)
    text(d, (142, 711), f"MEAN MINIMUM GAP   {q['min_gap']:.2f} m", 24, WHITE, True, True)
    text(d, (142, 748), f"TTC < 2 s share   {q['ttc']:.2f}%", 21, VIOLET, True, True)
    box(d, (1015, 680, 1809, 783), 17, (11, 22, 36), (47, 88, 91), 2)
    text(d, (1046, 711), f"MEAN MINIMUM GAP   {guarded['min_gap']:.2f} m", 24, WHITE, True, True)
    text(d, (1046, 748), f"TTC < 2 s share   {guarded['ttc']:.2f}%", 21, TEAL, True, True)
    box(d, (580, 817, 1342, 904), 22, (20, 36, 54), (76, 94, 117), 2)
    center(d, 961, 845, f"+{gap:.2f} m mean episode minimum gap", 23, AMBER, True, True)
    center(d, 961, 879, "Change measured across 50 matched cut-in seeds", 17, MUTED)
    footer(d, "RESULTS FROM SYNTHETIC CUT-IN FAMILY  /  NOT A VEHICLE TEST", (4 + local / duration) / 7)
    return image


def draw_scene_6(local, duration, summary):
    image, d = new_frame()
    header(d, "THE TRADE-OFF AND BENCHMARK", "06  /  READ ALL THREE METRICS")
    text(d, (84, 132), "More gap margin came with a rougher Q response.", 45, WHITE, True)
    text(d, (89, 198), "MPC remained stronger on minimum gap and mean absolute jerk in this test set.", 22, MUTED)
    names = [("CTG-PID", BLUE), ("Q-Learning", VIOLET), ("Q + guard", TEAL), ("MPC", AMBER)]
    x_positions = [356, 805, 1249, 1655]
    metrics = ["min_gap", "ttc", "jerk"]
    labels = [("MEAN MINIMUM GAP", "metres", 14.5), ("CLOSING SAMPLES\nWITH TTC < 2 s", "percent", 3.0), ("MEAN ABSOLUTE JERK", "m/s³", 1.35)]
    # Three horizontally aligned metric tracks; all displayed values are from CSV.
    for col, ((metric_title, units, maximum), metric) in enumerate(zip(labels, metrics)):
        x0 = 89 + col * 609
        box(d, (x0, 280, x0 + 568, 812), 23, (13, 27, 44), (45, 68, 91), 2)
        text(d, (x0 + 25, 307), metric_title, 19, TEAL if col == 0 else (VIOLET if col == 1 else AMBER), True, True)
        text(d, (x0 + 25, 355), units, 14, FAINT, False, True)
        for i, (name, color) in enumerate(names):
            entry_name = "Q+RSS" if name == "Q + guard" else name
            y = 426 + i * 82
            value = summary[entry_name][metric]
            label = f"{value:.2f}" if metric == "min_gap" else (f"{value:.2f}%" if metric == "ttc" else f"{value:.2f}")
            text(d, (x0 + 24, y), name.upper(), 15, color, True, True)
            bx0, bx1, by = x0 + 26, x0 + 388, y + 29
            box(d, (bx0, by, bx1, by + 15), 7, (28, 42, 58), None, 0)
            fill_w = max(3, int((bx1 - bx0) * min(1.0, max(0.0, value / maximum))))
            d.rounded_rectangle((bx0, by, bx0 + fill_w, by + 15), radius=7, fill=color)
            text(d, (x0 + 540, y + 24), label, 19, WHITE, True, True, anchor="ra")
    # Explicit interpretation callouts.
    q, guarded, mpc = summary["Q-Learning"], summary["Q+RSS"], summary["MPC"]
    jerk_increase = guarded["jerk"] - q["jerk"]
    min_gap_increase = guarded["min_gap"] - q["min_gap"]
    box(d, (88, 849, 1211, 930), 19, (13, 28, 44), (46, 73, 91), 2)
    text(d, (118, 880), f"Q + guard: +{min_gap_increase:.2f} m minimum gap", 21, TEAL, True)
    text(d, (617, 880), f"+{jerk_increase:.2f} m/s³ mean abs jerk", 21, AMBER, True)
    box(d, (1236, 849, 1832, 930), 19, (13, 28, 44), (82, 71, 59), 2)
    center(d, 1534, 879, f"MPC: {mpc['min_gap']:.2f} m minimum gap", 21, AMBER, True)
    center(d, 1534, 906, "and lower jerk than Q + guard", 15, MUTED)
    footer(d, "DESCRIPTIVE MEANS  /  50 SEED-MATCHED CUT-IN EPISODES PER CONTROLLER", (5 + local / duration) / 7)
    return image


def draw_scene_7(local, duration, summary):
    image, d = new_frame()
    header(d, "WHAT WE LEARNED", "07  /  SCOPE AND NEXT STEP")
    text(d, (84, 132), "A clear result. A deliberately narrow claim.", 47, WHITE, True)
    text(d, (89, 199), "A small, inspectable controls experiment that fits on a laptop.", 24, MUTED)
    # Characters reunite with their final review, the emotional close of the story.
    box(d, (85, 287, 1009, 815), 24, (13, 27, 44), (46, 68, 91), 2)
    person(d, 330, 346, 0.78, "mira", "listen", local)
    person(d, 682, 346, 0.78, "dev", "point", local)
    box(d, (166, 641, 918, 764), 19, (7, 18, 30), (53, 75, 96), 2)
    center(d, 542, 678, "NEXT: MEASURED CUT-IN REPLAY", 20, TEAL, True, True)
    center(d, 542, 725, "Add lane geometry, sensing and delay", 19, WHITE)
    # Honest scope panel.
    box(d, (1053, 287, 1837, 815), 24, (13, 27, 44), (46, 68, 91), 2)
    pill(d, 1090, 322, "WHAT WAS TESTED", TEAL, 237)
    scope = [
        ("1D point-mass model", BLUE),
        ("Instantaneous gap-step proxy", AMBER),
        ("No lane-change or perception model", VIOLET),
        ("No production-car head-to-head", RED),
    ]
    for i, (label, color) in enumerate(scope):
        y = 414 + i * 70
        d.ellipse((1101, y + 5, 1122, y + 26), fill=color)
        text(d, (1145, y + 15), label, 21, WHITE, True, anchor="lm")
    # Result-boundary statement.
    collisions = sum(summary[name]["collision"] for name in ("CTG-PID", "MPC", "Q-Learning", "Q+RSS"))
    note = "No collisions observed in these simulated cut-in runs. This is not a safety guarantee." if collisions == 0 else "Collision outcomes are simulation results, not road-safety evidence."
    box(d, (85, 864, 1837, 956), 20, (31, 26, 33), (110, 76, 70), 2)
    center(d, 961, 910, note, 25, AMBER, True)
    footer(d, "SMALL Q-LEARNING CORRECTION  +  SIMPLIFIED BRAKING CHECK  +  HONEST EVALUATION", (6 + local / duration) / 7)
    return image


def wrap(draw, value: str, fnt, max_width: int) -> list[str]:
    words = value.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def subtitle(image: Image.Image, paragraph: str):
    d = ImageDraw.Draw(image, "RGBA")
    d.rounded_rectangle((110, 948, W - 110, 1024), radius=17, fill=(5, 12, 20, 220), outline=(66, 84, 104, 210), width=1)
    fnt = font(22, False, False)
    lines = wrap(d, paragraph, fnt, W - 280)
    lines = lines[:2]
    y = 968 if len(lines) == 2 else 986
    for line in lines:
        d.text((W // 2, y), line, font=fnt, fill=(238, 244, 250, 255), anchor="mm")
        y += 29


def scene_image(index: int, local: float, duration: float, traces, summary) -> Image.Image:
    funcs = [
        lambda: draw_scene_1(local, duration),
        lambda: draw_scene_2(local, duration),
        lambda: draw_scene_3(local, duration),
        lambda: draw_scene_4(local, duration),
        lambda: draw_scene_5(local, duration, traces, summary),
        lambda: draw_scene_6(local, duration, summary),
        lambda: draw_scene_7(local, duration, summary),
    ]
    return funcs[index]()


def mix_audio(raw_voice_files: list[Path], speech_durations: list[float], pad_s: float,
              out_wav: Path, sample_rate=48000) -> list[SceneTiming]:
    timings, chunks = [], []
    cursor = 0.0
    voice_arrays = []
    for path, speech_s in zip(raw_voice_files, speech_durations):
        raw = np.fromfile(path, dtype="<i2").astype(np.float32) / 32768.0
        duration = len(raw) / sample_rate
        voice_arrays.append(raw)
        timings.append(SceneTiming(cursor, duration, cursor + duration + pad_s))
        chunks.append((raw, int(round(pad_s * sample_rate))))
        cursor += duration + pad_s

    total_samples = int(round(cursor * sample_rate))
    voice = np.zeros(total_samples, dtype=np.float32)
    cursor_samples = 0
    for raw, pad_samples in chunks:
        end = min(total_samples, cursor_samples + len(raw))
        voice[cursor_samples:end] = raw[:end - cursor_samples]
        cursor_samples += len(raw) + pad_samples

    # Original soft ambient bed; slow harmonic movement leaves the speech clear.
    t = np.arange(total_samples, dtype=np.float32) / sample_rate
    chord_roots = np.array([65.41, 55.0, 73.42, 49.0, 65.41], dtype=np.float32)
    chord_length = 16.0
    chord_ix = np.minimum((t / chord_length).astype(int), len(chord_roots) - 1)
    root = chord_roots[chord_ix]
    bed = np.zeros(total_samples, dtype=np.float32)
    for multiple, amp, detune in ((1.0, 0.42, 1.0), (1.5, 0.20, 1.003), (2.0, 0.14, 0.999), (3.0, 0.07, 1.001)):
        phase = 2 * np.pi * np.cumsum(root * multiple * detune) / sample_rate
        bed += amp * np.sin(phase).astype(np.float32)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * t / 12.0 - np.pi / 2)
    bed *= (0.25 + 0.75 * swell) * 0.055
    mix = voice * 0.82 + bed
    peak = float(np.max(np.abs(mix))) if len(mix) else 0.0
    if peak > 0.98:
        mix *= 0.98 / peak
    stereo = np.repeat(np.clip(mix, -1.0, 1.0)[:, None], 2, axis=1)
    pcm = (stereo * 32767).astype("<i2")
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())
    return timings


def write_srt(path: Path, timings: list[SceneTiming]):
    def stamp(seconds: float):
        ms = int(round(seconds * 1000))
        hh, ms = divmod(ms, 3_600_000)
        mm, ms = divmod(ms, 60_000)
        ss, ms = divmod(ms, 1000)
        return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"
    parts = []
    for i, timing in enumerate(timings):
        parts.extend([str(i + 1), f"{stamp(timing.start)} --> {stamp(timing.start + timing.speech)}", NARRATION[i], ""])
    path.write_text("\n".join(parts), encoding="utf-8")


def render_video(ffmpeg: str, output: Path, audio: Path, timings: list[SceneTiming],
                 traces, summary, fps: int):
    total_s = timings[-1].end
    total_frames = math.ceil(total_s * fps)
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{W}x{H}",
           "-framerate", str(fps), "-i", "pipe:0", "-i", str(audio),
           "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(output)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    scene_index = 0
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        while scene_index + 1 < len(timings) and t >= timings[scene_index].end:
            scene_index += 1
        timing = timings[scene_index]
        local = min(timing.end - timing.start, max(0.0, t - timing.start))
        scene_duration = timing.end - timing.start
        image = scene_image(scene_index, local, scene_duration, traces, summary)
        subtitle(image, NARRATION[scene_index])
        # Very short opening and end fades, with crisp cuts between evidence cards.
        fade = 1.0
        if frame_idx < round(0.38 * fps):
            fade = frame_idx / max(1.0, 0.38 * fps)
        if scene_index == len(timings) - 1 and t > total_s - 0.45:
            fade = min(fade, max(0.0, (total_s - t) / 0.45))
        if fade < 0.999:
            image = Image.blend(Image.new("RGB", (W, H), INK), image, max(0.0, fade))
        proc.stdin.write(image.tobytes())
    proc.stdin.close()
    code = proc.wait()
    if code:
        raise subprocess.CalledProcessError(code, cmd)
    return total_s


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, default=Path("outputs/formal_50seed/representative_traces.csv"))
    parser.add_argument("--summary", type=Path, default=Path("outputs/formal_50seed/scenario_summary.csv"))
    parser.add_argument("--output", type=Path, default=Path("workspace/output/ACC_RL_Story_Explainer.mp4"))
    parser.add_argument("--fps", type=int, default=FPS)
    parser.add_argument("--voice", default="Rishi (English (India))")
    parser.add_argument("--rate", type=int, default=168, help="macOS say speaking rate, in words per minute")
    parser.add_argument("--no-voiceover", action="store_true", help="Render clean ambient music only")
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required to encode the MP4.")
    traces = {name: load_csv(args.trace, "cut_in", name) for name in ("Q-Learning", "Q+RSS")}
    summary = load_summary(args.summary)
    if abs((summary["Q+RSS"]["min_gap"] - summary["Q-Learning"]["min_gap"]) - 4.35) > 0.03:
        raise ValueError("The story copy is calibrated for the current 50-seed gap result; update narration before rendering changed data.")
    if not args.no_voiceover and not shutil.which("say"):
        raise RuntimeError("macOS 'say' is unavailable. Use --no-voiceover or generate on the project Mac.")

    out = args.output
    temp_dir = Path("tmp/acc_story_video")
    temp_dir.mkdir(parents=True, exist_ok=True)
    ref_dir = out.parent / "ACC_RL_Character_References"
    write_character_references(ref_dir)
    audio_wav = temp_dir / "story_mix.wav"
    if args.no_voiceover:
        empty_segments = []
        for i in range(7):
            blank = temp_dir / f"blank_{i}.s16le"
            np.zeros(int(14.2 * 48000), dtype="<i2").tofile(blank)
            empty_segments.append(blank)
        # A no-voice fallback leaves an intentional ambient-only runtime of 15 s per scene.
        durations = [14.2] * 7
        raw_files = empty_segments
        pad_s = 0.8
    else:
        raw_files, durations = make_voice_segments(temp_dir, args.voice, args.rate, ffmpeg)
        pad_s = 0.9
    timings = mix_audio(raw_files, durations, pad_s, audio_wav)
    srt_path = out.with_suffix(".srt")
    write_srt(srt_path, timings)
    total_s = render_video(ffmpeg, out, audio_wav, timings, traces, summary, args.fps)
    # Save the opening as a poster with narration/subtitles removed for a clean thumbnail.
    poster = out.with_name(out.stem + "_Poster.png")
    first = scene_image(0, 3.2, max(1, timings[0].end - timings[0].start), traces, summary)
    first.save(poster, optimize=True)
    print(f"Wrote {out} · {total_s:.1f}s · {W}x{H} · {args.fps} fps · narrated with {args.voice if not args.no_voiceover else 'ambient-only audio'}")
    print(f"Wrote captions: {srt_path}")
    print(f"Wrote character references: {ref_dir}")


if __name__ == "__main__":
    main()
