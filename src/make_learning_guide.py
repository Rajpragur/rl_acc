"""Build a short, code-linked student guide to the ACC reinforcement-learning project."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/ACC_RL_Learning_Guide.pdf"
SUMMARY = ROOT / "outputs/formal_50seed/scenario_summary.csv"
PAGE_W, PAGE_H = A4

NAVY = colors.HexColor("#101C2E")
INK = colors.HexColor("#18283D")
MUTED = colors.HexColor("#61748B")
TEAL = colors.HexColor("#087E8B")
TEAL_LIGHT = colors.HexColor("#E7F5F4")
VIOLET = colors.HexColor("#7353C7")
AMBER = colors.HexColor("#B46A0A")
RED = colors.HexColor("#A84650")
BLUE = colors.HexColor("#376EAD")
PAPER = colors.HexColor("#F5F7FA")
LINE = colors.HexColor("#D8E0E8")
PALE = colors.HexColor("#EEF2F6")
WHITE = colors.white

STYLES = {
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.1,
        leading=13.0, textColor=INK, spaceAfter=3, alignment=TA_LEFT),
    "body_small": ParagraphStyle("body_small", fontName="Helvetica", fontSize=8.15,
        leading=11.1, textColor=INK, alignment=TA_LEFT),
    "body_white": ParagraphStyle("body_white", fontName="Helvetica", fontSize=10.0,
        leading=14.4, textColor=WHITE, alignment=TA_LEFT),
    "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.0,
        leading=10.4, textColor=INK, alignment=TA_LEFT),
    "cell_bold": ParagraphStyle("cell_bold", fontName="Helvetica-Bold", fontSize=8.0,
        leading=10.4, textColor=INK, alignment=TA_LEFT),
    "cell_white": ParagraphStyle("cell_white", fontName="Helvetica", fontSize=8.0,
        leading=10.4, textColor=WHITE, alignment=TA_LEFT),
    "center": ParagraphStyle("center", fontName="Helvetica", fontSize=8.0,
        leading=10, textColor=INK, alignment=TA_CENTER),
    "center_white": ParagraphStyle("center_white", fontName="Helvetica-Bold", fontSize=7.8,
        leading=9.5, textColor=WHITE, alignment=TA_CENTER),
}


def para(c: canvas.Canvas, text: str, x: float, top: float, width: float,
         style: ParagraphStyle | None = None) -> float:
    p = Paragraph(text, style or STYLES["body"])
    _, h = p.wrap(width, PAGE_H)
    p.drawOn(c, x, top - h)
    return top - h


def label(c, x, y, text, color=TEAL, size=8.2):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, text.upper())


def card(c, x, y, w, h, fill=WHITE, stroke=LINE, radius=9):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def page_frame(c, page_num: int, section: str, title: str, intro: str = "") -> float:
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.rect(0, PAGE_H - 8, PAGE_W, 8, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(TEAL)
    c.drawString(42, PAGE_H - 29, "ACC / RL   LEARNING GUIDE")
    c.setFont("Helvetica", 8)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - 42, PAGE_H - 29, f"{page_num:02d} / 05")
    label(c, 42, PAGE_H - 58, section, TEAL, 8)
    p = Paragraph(title, ParagraphStyle("page_title", fontName="Helvetica-Bold",
        fontSize=23, leading=27, textColor=NAVY, spaceAfter=0))
    _, th = p.wrap(PAGE_W - 84, 90)
    p.drawOn(c, 42, PAGE_H - 69 - th)
    y = PAGE_H - 78 - th
    if intro:
        y = para(c, intro, 43, y, PAGE_W - 86, STYLES["body"])
    c.setStrokeColor(LINE)
    c.line(42, 38, PAGE_W - 42, 38)
    c.setFont("Helvetica", 7.4)
    c.setFillColor(MUTED)
    c.drawString(42, 24, "Course project explainer  |  Point-mass simulation  |  Not vehicle validation")
    c.drawRightString(PAGE_W - 42, 24, str(page_num))
    return y - 15


def draw_table(c, data, x, top, widths, style=None, row_heights=None):
    table = Table(data, colWidths=widths, rowHeights=row_heights, repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
    ]
    for row in range(1, len(data)):
        commands.append(("BACKGROUND", (0, row), (-1, row), WHITE if row % 2 else PALE))
    if style:
        commands.extend(style)
    table.setStyle(TableStyle(commands))
    _, h = table.wrap(sum(widths), PAGE_H)
    table.drawOn(c, x, top - h)
    return top - h


def section(c, x, y, title, color=TEAL):
    label(c, x, y, title, color, 8.3)
    c.setStrokeColor(LINE)
    c.line(x, y - 5, PAGE_W - 42, y - 5)
    return y - 17


def load_cut_in_summary():
    rows = {}
    with SUMMARY.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["scenario"] == "cut_in":
                rows[row["controller"]] = row
    wanted = {"CTG-PID", "MPC", "Q-Learning", "Q+RSS"}
    if not wanted.issubset(rows):
        raise ValueError(f"Cut-in summary is missing: {wanted - set(rows)}")
    if any(int(rows[name]["episodes"]) != 50 for name in wanted):
        raise ValueError("This guide is written for 50 matched cut-in episodes per controller.")
    return rows


def page_one(c, results):
    y = page_frame(c, 1, "01 / PROJECT IN ONE MINUTE",
        "A small learning layer inside<br/>a familiar ACC controller",
        "This project asks whether a small tabular Q-learning correction, paired with a braking-distance action filter, can improve a classical adaptive cruise controller in a sudden-gap stress case.")

    label(c, 44, y - 2, "THE CLOSED-LOOP SIMULATION", TEAL)
    flow_y, flow_h = y - 142, 86
    boxes = [
        ("LEAD CAR", "scripted speed,\nbraking and gap event", BLUE),
        ("OBSERVATION", "gap error, speeds\nand acceleration", TEAL),
        ("CONTROLLER", "PID + Q correction\noptional guard", VIOLET),
        ("EGO VEHICLE", "actuator lag, drag,\nrolling resistance", AMBER),
    ]
    left, box_w, gap = 44, 112, 18
    for i, (head, body, color) in enumerate(boxes):
        x = left + i * (box_w + gap)
        card(c, x, flow_y, box_w, flow_h, WHITE, LINE, 8)
        c.setFillColor(color)
        c.roundRect(x, flow_y + flow_h - 5, box_w, 5, 3, fill=1, stroke=0)
        c.setFillColor(color)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(x + 8, flow_y + flow_h - 23, head)
        para(c, body.replace("\n", "<br/>"), x + 8, flow_y + flow_h - 30,
             box_w - 16, STYLES["body_small"])
        if i < 3:
            ax = x + box_w + 3
            c.setStrokeColor(MUTED)
            c.setLineWidth(1.3)
            c.line(ax, flow_y + flow_h / 2, ax + 11, flow_y + flow_h / 2)
            c.line(ax + 7, flow_y + flow_h / 2 + 3, ax + 11, flow_y + flow_h / 2)
            c.line(ax + 7, flow_y + flow_h / 2 - 3, ax + 11, flow_y + flow_h / 2)

    qmin = float(results["Q-Learning"]["min_gap_m_mean"])
    gmin = float(results["Q+RSS"]["min_gap_m_mean"])
    qttc = float(results["Q-Learning"]["ttc_below_2s_pct_mean"])
    gttc = float(results["Q+RSS"]["ttc_below_2s_pct_mean"])
    qjerk = float(results["Q-Learning"]["mean_abs_jerk_mps3_mean"])
    gjerk = float(results["Q+RSS"]["mean_abs_jerk_mps3_mean"])

    call_y, call_h = flow_y - 118, 94
    card(c, 44, call_y, PAGE_W - 88, call_h, NAVY, NAVY, 10)
    label(c, 62, call_y + call_h - 24, "THE RESEARCH QUESTION", TEAL_LIGHT, 7.8)
    para(c, "When the following gap drops suddenly, does filtering a tabular RL controller's proposed acceleration improve its response?",
         62, call_y + call_h - 39, PAGE_W - 125, STYLES["body_white"])

    stats_y, stats_h = call_y - 133, 112
    label(c, 44, stats_y + stats_h + 12, "WHAT 50 MATCHED CUT-IN RUNS SHOWED", TEAL)
    stat_specs = [
        ("MINIMUM GAP", f"+{gmin-qmin:.2f} m", "Q + guard vs Q", TEAL),
        ("SHORT-TTC SHARE", f"{qttc:.2f}% -> {gttc:.0f}%", "closing samples under 2 s", VIOLET),
        ("RIDE TRADE-OFF", f"{qjerk:.3f} -> {gjerk:.3f}", "mean absolute jerk, m/s^3", AMBER),
    ]
    stat_w = (PAGE_W - 88 - 16) / 3
    for i, (head, value, note, color) in enumerate(stat_specs):
        x = 44 + i * (stat_w + 8)
        card(c, x, stats_y, stat_w, stats_h, WHITE, LINE, 8)
        label(c, x + 10, stats_y + stats_h - 19, head, color, 6.8)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 15.4 if i != 1 else 13.5)
        c.drawString(x + 10, stats_y + 53, value)
        para(c, note, x + 10, stats_y + 43, stat_w - 20, STYLES["body_small"])

    card(c, 44, 69, PAGE_W - 88, 42, TEAL_LIGHT, TEAL_LIGHT, 7)
    para(c, "<b>Scope:</b> The cut-in is an instantaneous longitudinal gap change. There is no lane-change geometry, perception model, or production-car head-to-head.",
         55, 101, PAGE_W - 110, STYLES["body_small"])
    c.showPage()


def page_two(c):
    y = page_frame(c, 2, "02 / CONTROLLER AND LEARNING",
        "What each controller actually does",
        "The learned policy does not steer or replace the whole controller. It adds one small acceleration correction to a transparent spacing controller; an optional filter can then alter that command.")

    data = [
        ["CONTROLLER", "ROLE IN THIS PROJECT"],
        [Paragraph("<b>CTG-PID</b><br/>classical baseline", STYLES["cell"]),
         Paragraph("Targets a time gap: <b>desired distance = 5 m + 1.3 x ego speed</b>. A proportional gap term and relative-speed term produce a bounded acceleration command.", STYLES["cell"])],
        [Paragraph("<b>Q-learning</b><br/>tabular residual", STYLES["cell"]),
         Paragraph("Chooses one of seven residual accelerations and adds it to CTG-PID's proposed command. The learned object is a table of state-action values, not a large neural network.", STYLES["cell"])],
        [Paragraph("<b>Q + guard</b><br/>filtered action", STYLES["cell"]),
         Paragraph("Checks the proposed command against a simplified stopping-distance margin. If it fails, a bounded search selects the least-braking command that passes the check.", STYLES["cell"])],
        [Paragraph("<b>MPC</b><br/>predictive reference", STYLES["cell"]),
         Paragraph("Tests candidate commands using a short forward model of spacing, speed difference, acceleration and jerk. It is a simple model-based reference, not an OEM ACC system.", STYLES["cell"])],
    ]
    bottom = draw_table(c, data, 44, y, [106, PAGE_W - 88 - 106])

    y = section(c, 44, bottom - 24, "THE Q-LEARNING TABLE HAS THREE PARTS")
    gap = 8
    box_w = (PAGE_W - 88 - gap * 2) / 3
    cards = [
        ("STATE", "5 binned signals:<br/>gap error, closing speed, ego speed, ego acceleration, and lead acceleration.", TEAL),
        ("ACTION", "7 residual accelerations:<br/>-1.2, -0.6, -0.25, 0, +0.25, +0.6, +1.2 m/s^2.", VIOLET),
        ("REWARD", "Favors desired spacing and smooth motion; penalizes closing speed, weak stopping margin and collision.", AMBER),
    ]
    box_y, box_h = y - 133, 118
    for i, (head, body, color) in enumerate(cards):
        x = 44 + i * (box_w + gap)
        card(c, x, box_y, box_w, box_h, WHITE, LINE, 8)
        label(c, x + 10, box_y + box_h - 20, head, color, 7.1)
        para(c, body, x + 10, box_y + box_h - 32, box_w - 20, STYLES["body_small"])

    eq_y, eq_h = box_y - 92, 71
    card(c, 44, eq_y, PAGE_W - 88, eq_h, TEAL_LIGHT, TEAL_LIGHT, 8)
    label(c, 57, eq_y + eq_h - 19, "Q-LEARNING UPDATE", TEAL, 7.1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(57, eq_y + 30, "Q(s,a) <- Q(s,a) + alpha [ reward + gamma max Q(next state) - Q(s,a) ]")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.8)
    c.drawString(57, eq_y + 13, "Training uses alpha = 0.12, gamma = 0.985, and epsilon-greedy exploration that decays from 1.0 to 0.05.")

    note_bottom = para(c, "Training profiles are steady speed, a smooth speed wave, and moderate lead-car braking. The cut-in and emergency profiles are held out for evaluation.",
         45, eq_y - 14, PAGE_W - 90, STYLES["body_small"])
    light_y = note_bottom - 81
    card(c, 44, light_y, PAGE_W - 88, 72, TEAL_LIGHT, TEAL_LIGHT, 8)
    label(c, 57, light_y + 54, "WHY THIS STAYS LIGHTWEIGHT", TEAL, 7.1)
    para(c, "The binned state space has 9 x 10 x 8 x 7 x 7 = 35,280 states. With 7 actions, the learned table stores 246,960 values - compact enough to inspect without a deep network or GPU.",
         57, light_y + 42, PAGE_W - 114, STYLES["body_small"])
    c.showPage()


def page_three(c):
    y = page_frame(c, 3, "03 / SIMULATION AND EXPERIMENT DESIGN",
        "Learn on routine driving; test stressful events separately",
        "The experiment compares methods under matched initial conditions. Every method gets the same event parameters for a given seed, so the comparison is paired rather than a set of unrelated runs.")

    card(c, 44, y - 93, PAGE_W - 88, 76, NAVY, NAVY, 9)
    label(c, 58, y - 37, "FORMAL EVALUATION", TEAL_LIGHT, 7.6)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(58, y - 62, "50 seeds x 5 scenarios x 4 controllers = 1,000 episodes")
    c.setFillColor(colors.HexColor("#CCD8E6"))
    c.setFont("Helvetica", 8.3)
    c.drawString(58, y - 79, "Each episode: 40 seconds at 0.1-second steps. Controllers share each seed's start and event.")

    table_top = y - 113
    data = [
        ["SCENARIO", "WHAT HAPPENS", "ROLE"],
        ["Steady", "Lead speed stays approximately constant.", "Training + evaluation"],
        ["Wave", "Lead speed varies smoothly around its base speed.", "Training + evaluation"],
        ["Moderate brake", "Lead vehicle slows and later recovers.", "Training + evaluation"],
        ["Cut-in", "Gap drops instantly by 16-26 m; lead then brakes.", "Held-out test"],
        ["Emergency", "Higher-speed case with stronger lead braking.", "Held-out test"],
    ]
    data = [[Paragraph(x, STYLES["cell_white"] if r == 0 else STYLES["cell"]) for x in row]
            for r, row in enumerate(data)]
    bottom = draw_table(c, data, 44, table_top, [83, 294, PAGE_W - 88 - 377])
    y = section(c, 44, bottom - 21, "WHAT THE SIMULATOR INCLUDES")

    settings = [
        ("VEHICLE", "1,500 kg point mass; acceleration command limited to -6 to +2.5 m/s^2."),
        ("ACTUATOR", "First-order lag with a 0.35 s time constant."),
        ("ROAD LOAD", "Aerodynamic drag and rolling resistance."),
        ("GAP RULE", "5 m standstill spacing + 1.3 s time gap at ego speed."),
    ]
    for i, (head, body) in enumerate(settings):
        x = 44 + (i % 2) * 257
        yy = y - (i // 2) * 68 - 47
        card(c, x, yy, 249, 56, WHITE, LINE, 7)
        label(c, x + 10, yy + 39, head, TEAL if i % 2 == 0 else VIOLET, 6.8)
        para(c, body, x + 10, yy + 30, 229, STYLES["body_small"])

    glossary_top = y - 198
    label(c, 44, glossary_top, "METRICS TO READ", TEAL, 8.1)
    metric_data = [
        ["METRIC", "PLAIN-LANGUAGE MEANING"],
        ["Minimum gap", "Smallest recorded bumper-to-bumper spacing in an episode."],
        ["TTC under 2 s", "Share of closing samples where gap / closing speed is below 2 seconds."],
        ["Mean absolute jerk", "Average size of acceleration change per second; a rough ride-smoothness proxy."],
        ["Gap RMSE", "How closely measured gap follows the desired time-gap target."],
    ]
    metric_data = [[Paragraph(x, STYLES["cell_white"] if r == 0 else STYLES["cell"]) for x in row]
                   for r, row in enumerate(metric_data)]
    draw_table(c, metric_data, 44, glossary_top - 11, [111, PAGE_W - 88 - 111])
    c.showPage()


def page_four(c, results):
    y = page_frame(c, 4, "04 / RESULTS AND INTERPRETATION",
        "What happened in the 50 cut-in episodes",
        "The cut-in family is a synthetic holdout: the Q table was trained on steady, wave, and moderate-braking profiles, not on cut-in episodes.")

    order = ["CTG-PID", "Q-Learning", "Q+RSS", "MPC"]
    names = {"CTG-PID": "Classical CTG-PID", "Q-Learning": "Q-learning", "Q+RSS": "Q + braking guard", "MPC": "Predictive MPC"}
    data = [[
        Paragraph("METHOD", STYLES["cell_white"]),
        Paragraph("MIN GAP<br/>(m)", STYLES["center_white"]),
        Paragraph("TTC UNDER 2 s<br/>(%)", STYLES["center_white"]),
        Paragraph("ABS JERK<br/>(m/s^3)", STYLES["center_white"]),
        Paragraph("GAP RMSE<br/>(m)", STYLES["center_white"]),
    ]]
    for name in order:
        r = results[name]
        data.append([
            Paragraph(names[name], STYLES["cell_bold"]),
            f"{float(r['min_gap_m_mean']):.2f}",
            f"{float(r['ttc_below_2s_pct_mean']):.2f}",
            f"{float(r['mean_abs_jerk_mps3_mean']):.3f}",
            f"{float(r['gap_rmse_m_mean']):.2f}",
        ])
    bottom = draw_table(c, data, 44, y, [139, 77, 88, 101, PAGE_W - 88 - 405])

    q = results["Q-Learning"]
    guarded = results["Q+RSS"]
    mpc = results["MPC"]
    qmin, gmin = float(q["min_gap_m_mean"]), float(guarded["min_gap_m_mean"])
    qttc, gttc = float(q["ttc_below_2s_pct_mean"]), float(guarded["ttc_below_2s_pct_mean"])
    qjerk, gjerk = float(q["mean_abs_jerk_mps3_mean"]), float(guarded["mean_abs_jerk_mps3_mean"])

    take_y, take_h = bottom - 119, 99
    card(c, 44, take_y, PAGE_W - 88, take_h, TEAL_LIGHT, TEAL_LIGHT, 8)
    label(c, 58, take_y + take_h - 19, "READ THE TRADE-OFF", TEAL, 7.5)
    para(c,
         f"<b>Q + guard vs Q:</b> mean episode minimum gap rises by {gmin-qmin:.2f} m; closing-sample TTC-under-2 share changes from {qttc:.2f}% to {gttc:.0f}%.<br/><b>Comfort cost:</b> mean absolute jerk changes from {qjerk:.3f} to {gjerk:.3f} m/s^3.<br/><b>Reference:</b> MPC has the largest mean minimum gap ({float(mpc['min_gap_m_mean']):.2f} m) and the lowest cut-in gap RMSE ({float(mpc['gap_rmse_m_mean']):.2f} m).",
         58, take_y + take_h - 31, PAGE_W - 116, STYLES["body_small"])

    limit_y, limit_h = take_y - 108, 91
    card(c, 44, limit_y, PAGE_W - 88, limit_h, WHITE, LINE, 8)
    label(c, 58, limit_y + limit_h - 19, "WHAT YOU CANNOT CLAIM", RED, 7.4)
    para(c,
         "No collisions were observed in these 50 runs, but this is not a risk estimate or safety proof. The guard is RSS-inspired, not a formal RSS implementation. CTG-PID is a classical simulated baseline; no production vehicle was tested under matched conditions.",
         58, limit_y + limit_h - 31, PAGE_W - 116, STYLES["body_small"])
    para(c,
         "A separate 2025 Honda Accord manual describes warnings for abrupt lead-vehicle deceleration and cut-ins. That is feature context only, not evidence that this controller outperforms a commercial ACC system.",
         45, limit_y - 15, PAGE_W - 90, STYLES["body_small"])

    report_y = 118
    card(c, 44, report_y, PAGE_W - 88, 118, PALE, LINE, 8)
    label(c, 58, report_y + 99, "REPORTING TIP", VIOLET, 7.4)
    para(c,
         "Report episode means and spread, not one representative seed. For a matched-method claim, use the per-seed deltas in <b>paired_differences.csv</b>. The displayed 95% intervals are descriptive normal approximations, not significance tests. Describe the TTC result as a share of closing samples under two seconds.",
         58, report_y + 86, PAGE_W - 116, STYLES["body_small"])
    c.showPage()


def page_five(c):
    y = page_frame(c, 5, "05 / RUN IT AND EXPLORE THE CODE",
        "A practical route through the project",
        "The simulator and tabular policy run on CPU. The formal batch previously used about 42 MB peak resident memory on this machine. MP4 rendering requires FFmpeg in addition to the Python packages.")

    commands = [
        ("1. Install the project packages", "python3 -m venv .venv<br/>source .venv/bin/activate<br/>python -m pip install -r requirements.txt"),
        ("2. Train the Q table", "python src/train_q_learning.py --episodes 6000 --seed 17 --output models/q_agent.npz"),
        ("3. Evaluate matched episodes", "python src/run_experiments.py --seeds 50 --output outputs/formal_50seed"),
        ("4. Render the explainer", "python src/make_explainer_video.py --output workspace/output/ACC_CutIn_Explainer.mp4"),
    ]
    cy = y - 14
    for title, command in commands:
        h = 64 if "Install" not in title else 77
        cy -= h
        card(c, 44, cy, PAGE_W - 88, h, WHITE, LINE, 7)
        label(c, 56, cy + h - 17, title, TEAL, 7.2)
        p = Paragraph(command, ParagraphStyle("cmd", fontName="Courier", fontSize=7.5,
            leading=10.1, textColor=NAVY))
        _, ph = p.wrap(PAGE_W - 116, h)
        p.drawOn(c, 56, cy + 8)
        cy -= 8

    map_top = cy - 9
    label(c, 44, map_top, "START HERE IN THE SOURCE TREE", TEAL, 8.1)
    file_data = [
        ["FILE", "PURPOSE"],
        ["src/acc_sim.py", "Vehicle model, scenarios, CTG-PID, guard, MPC, metrics."],
        ["src/train_q_learning.py", "Exploration, reward and Q-table update."],
        ["src/run_experiments.py", "Matched seeds, scenario summaries and trace export."],
        ["src/make_explainer_video.py", "Plots the recorded cut-in trace and 50-seed results."],
        ["outputs/formal_50seed/", "Reproducible metrics, manifest, traces and comparison clips."],
    ]
    file_data = [[Paragraph(x, STYLES["cell_white"] if r == 0 else STYLES["cell"]) for x in row]
                 for r, row in enumerate(file_data)]
    bottom = draw_table(c, file_data, 44, map_top - 11, [171, PAGE_W - 88 - 171])

    next_top = bottom - 18
    card(c, 44, next_top - 55, PAGE_W - 88, 55, PALE, LINE, 7)
    label(c, 56, next_top - 18, "KEEP LEARNING", VIOLET, 7)
    para(c, "Read README.md first; use the 19-page project guide for literature and method detail; use the focused presentation for the class narrative. Dataset notes explain why the public traces are context, not a matched cut-in benchmark.",
         56, next_top - 25, PAGE_W - 112, STYLES["body_small"])
    c.showPage()


def main():
    results = load_cut_in_summary()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    c.setTitle("ACC with a Small Q-Learning Correction - Student Learning Guide")
    c.setAuthor("ACC Course Project")
    c.setSubject("How the adaptive cruise control reinforcement learning project works")
    page_one(c, results)
    page_two(c)
    page_three(c)
    page_four(c, results)
    page_five(c)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    main()
