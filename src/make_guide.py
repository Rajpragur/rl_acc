"""Build the course-project handbook PDF from the measured project run."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether, HRFlowable,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "ACC_RL_Project_Guide.pdf"
NAVY = colors.HexColor("#102437")
INK = colors.HexColor("#203243")
MUTED = colors.HexColor("#607487")
TEAL = colors.HexColor("#0E9F94")
PALE = colors.HexColor("#EAF4F4")
PALE_BLUE = colors.HexColor("#EEF3F7")
AMBER = colors.HexColor("#D58A24")
RED = colors.HexColor("#B34F49")
RULE = colors.HexColor("#D8E1E8")
PAGE_W, PAGE_H = A4
LEFT = RIGHT = 16 * mm
TOP = 19 * mm
BOTTOM = 17 * mm
WIDTH = PAGE_W - LEFT - RIGHT

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=28, leading=32, textColor=NAVY, alignment=TA_LEFT, spaceAfter=10))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=19, textColor=MUTED, spaceAfter=12))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=5, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.2, leading=15, textColor=TEAL, spaceBefore=10, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13.1, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=10.5, textColor=INK, spaceAfter=3))
styles.add(ParagraphStyle(name="Tinyx", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.2, leading=9, textColor=INK, spaceAfter=2))
styles.add(ParagraphStyle(name="Calloutx", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=NAVY, leftIndent=2, rightIndent=2, spaceAfter=1))
styles.add(ParagraphStyle(name="QuoteX", parent=styles["BodyText"], fontName="Helvetica-Oblique", fontSize=9.5, leading=13, textColor=MUTED, leftIndent=10, rightIndent=10, spaceAfter=7))
styles.add(ParagraphStyle(name="CellHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9, textColor=colors.white, spaceAfter=0))
styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.3, leading=9.2, textColor=INK, spaceAfter=0))
styles.add(ParagraphStyle(name="Ref", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=10.4, textColor=INK, leftIndent=10, firstLineIndent=-10, spaceAfter=5))
styles.add(ParagraphStyle(name="Footerx", parent=styles["Normal"], fontName="Helvetica", fontSize=7.5, leading=9, textColor=MUTED))


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def safe(text, style="Bodyx"):
    return P(escape(str(text)), style)


def bullet(text, style="Bodyx"):
    return Paragraph("&#8226;&nbsp; " + text, styles[style])


def cell(text, header=False):
    return Paragraph(str(text), styles["CellHead" if header else "Cell"])


def grid_table(rows, widths, header=True, font_size=7.3, padd=5):
    body = []
    for ridx, row in enumerate(rows):
        body.append([cell(x, header and ridx == 0) for x in row])
    t = Table(body, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), padd),
        ("RIGHTPADDING", (0, 0), (-1, -1), padd),
        ("TOPPADDING", (0, 0), (-1, -1), padd),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padd),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), NAVY)]
        if len(rows) > 1:
            commands += [("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE_BLUE])]
    t.setStyle(TableStyle(commands))
    return t


def callout(text, bg=PALE, accent=TEAL):
    t = Table([[P(text, "Calloutx")]], colWidths=[WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.5, RULE),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 7 * mm, PAGE_W, 7 * mm, stroke=0, fill=1)
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 7 * mm, 42 * mm, 1.3 * mm, stroke=0, fill=1)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(LEFT, 8 * mm, "ACC + tabular Q-learning | Project handbook")
    canvas.drawRightString(PAGE_W - RIGHT, 8 * mm, f"{doc.page}")
    canvas.restoreState()


def link(label, url):
    return f'<link href="{url}" color="#0E817A">{escape(label)}</link>'


def doi(code):
    return link("doi:" + code, "https://doi.org/" + code)


def build_story():
    s = []
    s += [Spacer(1, 26 * mm), P("AUTOMOTIVE TECHNOLOGY · PROJECT HANDBOOK", "H2x"),
          P("Reinforcement Learning<br/>for Adaptive Cruise Control", "CoverTitle"),
          P("A cut-in case study, 1,000 matched simulation episodes, commercial ACC context and research-paper analysis workbook", "CoverSub"),
          HRFlowable(width="100%", thickness=2, color=TEAL, spaceBefore=4, spaceAfter=14),
          P("A practical companion to the presentation", "H2x"),
          P("Use this guide to explain the automotive problem, compare prior evidence, defend the method, interpret the measured results and answer questions without overstating what a classroom simulator can prove.", "Bodyx"),
          Spacer(1, 7 * mm), callout("The direct answer is nuanced: the braking-distance guard improved two cut-in indicators compared with unguarded Q, but MPC still tracked better and left the largest minimum gap. Guarded Q also produced more jerk. We do not claim it beats a current commercial ACC vehicle."),
          Spacer(1, 12 * mm),
          P("Team members: add names before presenting", "Bodyx"),
          P("Prepared 16 October 2026 · Simulation results are generated by the included Python project", "Smallx"),
          PageBreak()]

    s += [P("How to use this handbook", "H1x"),
          P("Read the grading note first. Then use the paper analyses to write your literature review, the methods/results sections to explain your own experiment, the talk track to rehearse, and the worksheets to verify that each claim is supported. The source presentation and guide were used as course instructions; the WhatsApp text was treated as the team's actual project request.", "Bodyx"),
          P("What the attached grading guide says", "H2x"),
          grid_table([
              ["Assessment component", "Marks indicated in supplied guide", "What to show"],
              ["Literature review", "30–35", "Organized themes, accurate paper comparisons, critical synthesis, relevant gap and citations."],
              ["Own work / findings", "10", "A clear contribution, working simulation, documented design choices and an honest result, including negative findings."],
              ["Actual research", "30–35", "A question, reproducible method, fair baselines, repeated trials, measurements, analysis and limitations."],
          ], [43*mm, 35*mm, WIDTH-78*mm]),
          Spacer(1, 3*mm),
          callout("The figures 30–35 are marks, not a demand to review 30–35 papers. The supplied guide recommends a focused set of about 13 papers. This handbook reviews a broader core set of ACC, RL and safety sources so the team can select the most relevant papers for its final written submission.", bg=colors.HexColor("#FFF4E4"), accent=AMBER),
          P("A simple rule for full-credit work", "H2x"),
          bullet("Tell the reader what each study asked, how it tested the question, what evidence it reported and what that evidence cannot establish."),
          bullet("Separate your simulation result from a published result; label every metric with the scenario, sample count and unit."),
          bullet("Use the conclusion to answer your research question, not to claim that RL is universally better or that the guard makes a car safe."),
          bullet("Put the source and the caveat together. A strong citation is traceable and correctly scoped."),
          P("One-sentence project claim", "H2x"),
          callout("In a simplified 10 Hz point-mass car-following simulation, residual tabular Q-learning did not outperform CTG-PID or a one-move MPC; an RSS-inspired braking-distance filter reduced short-TTC exposure in the synthetic cut-in holdout, while leaving comfort, model-validity and formal-safety questions open."),
          PageBreak()]

    s += [P("1. Project definition", "H1x"),
          P("Adaptive Cruise Control (ACC) maintains a chosen speed when traffic is clear and regulates longitudinal spacing when a lead vehicle is detected. This project narrows that familiar task to one easy-to-picture event: another car joins the lane, the gap suddenly becomes shorter, and ACC has to reduce closing speed without making a sharp, uncomfortable response. The topic remains automotive because it includes vehicle dynamics, time-gap policy, actuator lag, braking limits, jerk and time-to-collision.", "Bodyx"),
          P("Research question", "H2x"),
          callout("Across randomized cut-in episodes, does a small tabular Q-learning correction plus a braking-distance guard improve minimum gap and short-TTC exposure compared with the same Q policy without the guard, and what does it cost in jerk and tracking?"),
          P("Sub-questions", "H2x"),
          bullet("How do tracking error and mean absolute jerk change across ordinary following, speed-wave and moderate-braking scenarios?"),
          bullet("How much does the gap and lead braking vary across the 50 matched cut-in seeds?"),
          bullet("How does the guard change short-TTC exposure, minimum gap, jerk and the number of actions it edits?"),
          bullet("Does the learned controller beat CTG-PID, a simplified MPC or the public commercial-ACC reference?"),
          P("Scope boundary", "H2x"),
          P("This is a deterministic teaching simulator, not a vehicle test. It has no lateral lane-change path, radar/camera perception, communication, road grade, tire limits, driver interaction, hardware, or parameter uncertainty outside the seeded setup ranges. A cut-in is approximated as an instantaneous 16–26 m reduction in longitudinal gap at 6–10 s, followed by 3.5–5.0 m/s² lead braking for 2–3 s. Do not describe it as a simulated lane change.", "Bodyx"),
          P("Production ACC and public field reference", "H2x"),
          P("A current product manual provides a feature-level comparison. The 2025 Honda Accord Hybrid manual describes a selectable following interval and a warning when the lead slows abruptly or another vehicle cuts in. The manual does not publish the proprietary acceleration-control map, so we cannot run that exact controller in our simulator. The EU JRC OpenACC database offers a public real-road reference: one Vicolungo recording has a human-driven Mitsubishi SpaceStar followed by a Ford S-Max with ACC at minimum distance setting. In 5,505 interpolated samples spanning 550.4 s, median time headway is 1.314 s. Our 5 m + 1.3v target is equivalent to 1.459 s at that recording's median follower speed of 31.36 m/s. This is a descriptive reference from one 2019 run, not a matched cut-in test or a claim about all current vehicles. " + link("Honda 2025 owner manual", "https://techinfo.honda.com/rjanisis/pubs/om/ah/a30b2525iom/enu/details/131245047-520366.html") + " · " + link("JRC OpenACC dataset", "https://data.jrc.ec.europa.eu/dataset/9702c950-c80f-4d2f-982f-44d06ea0009f") + " · " + link("OpenACC paper", "https://doi.org/10.1016/j.trc.2021.103047"), "Smallx"),
          P("Dataset selection and memory budget", "H2x"),
          P("We checked Hugging Face for cut-in data. Automingo-VQA includes images of cut-in events but the listed download is about 21.7 GB and it is a visual question-answering dataset rather than longitudinal control trajectories, so it was not downloaded under the team's 3–4 GB allowance. A small official OpenACC trajectory trace was a better fit for a headway reference. The simulation itself uses NumPy on CPU and does not require a GPU or a large language model.", "Smallx"),
          P("Recommended title", "H2x"),
          callout("Can a Small RL Correction Help ACC Handle a Cut-In? A 1,000-Episode Comparison with Classical Control"),
          PageBreak()]

    s += [P("2. How to conduct and write the literature review", "H1x"),
          P("Purpose", "H2x"),
          P("A literature review is an argument built from sources, not a sequence of unrelated abstracts. Organize the evidence around the engineering tension: classical ACC controllers are interpretable and tunable; RL can adapt a policy from interaction or data; safety layers attempt to constrain actions; generalization and real-world validation remain difficult.", "Bodyx"),
          P("Search and selection record", "H2x"),
          grid_table([
              ["Item", "Recommended record for this project"],
              ["Question", "How do classical ACC, reinforcement learning and action-filter methods trade tracking, comfort, safety indicators and robustness?"],
              ["Source types", "Peer-reviewed journal and conference papers, review articles, foundational method papers, and official ISO scope pages."],
              ["Search terms", "adaptive cruise control; car-following; model predictive control; reinforcement learning; deep RL; safety filter; RSS; control barrier function; string stability."],
              ["Inclusion", "Direct ACC/car-following relevance; clearly identified simulation, naturalistic-data or vehicle-test setting; sufficient method and result detail to compare."],
              ["Exclusion", "Untraceable claims, papers with no accessible method/result record, unrelated lane-keeping/perception work, and marketing claims without technical evidence."],
              ["Extraction", "Research question; vehicle/model/data; controller; baseline; scenarios; measures; key result; limitation; link to our design."],
          ], [39*mm, WIDTH-39*mm]),
          Spacer(1, 3*mm),
          P("Important scope note", "H2x"),
          P("The source list below is a structured, research-informed review prepared from publisher, author and standards records and the supplied course documents. Before submitting a formal paper, open the full text of the papers you cite and confirm every fine-grained numerical claim against its methods and result tables. Abstract-only information is not enough to support a detailed causal claim.", "Bodyx"),
          P("How to synthesize instead of listing papers", "H2x"),
          bullet("Compare studies that use similar tasks but different evidence: simulation versus naturalistic trajectories versus real vehicles."),
          bullet("Group by technical question: tracking and string stability; learning a car-following policy; safety filtering and operational limits."),
          bullet("Name a trade-off or disagreement: tracking error versus jerk, sample efficiency versus flexibility, or nominal performance versus holdout behavior."),
          bullet("End each theme with what remains unresolved and identify exactly which part your experiment examines."),
          PageBreak()]

    s += [P("3. Technical foundation", "H1x"),
          P("Longitudinal spacing", "H2x"),
          P("The ego vehicle follows at gap d and speed v. The desired distance in our implementation is d* = 5 + 1.3v metres. A useful spacing error is e = d − d*. The nominal CTG-PID baseline uses relative speed and spacing error; it is a transparent feedback rule, not a production controller.", "Bodyx"),
          P("Ego dynamics", "H2x"),
          callout("a = u_actuator − f_resistance(v)     |     v[k+1] = max(0, v[k] + a[k] Δt)     |     d[k+1] = d[k] + 0.5(v_lead + v_lead,next − v − v_next)Δt"),
          P("The point-mass simulator uses 1,500 kg mass, aerodynamic drag and rolling resistance, Δt = 0.1 s, a first-order actuator with 0.35 s time constant, and command bounds −6 to +2.5 m/s². These choices make the control experiment understandable, while leaving out important real-vehicle dynamics.", "Bodyx"),
          P("What the learner observes and controls", "H2x"),
          grid_table([
              ["Design item", "This implementation"],
              ["State", "Five normalized, discretized values: gap error; closing speed; ego speed; actual ego acceleration; estimated lead acceleration."],
              ["Action", "One of seven residual accelerations: −1.2, −0.6, −0.25, 0, +0.25, +0.6 or +1.2 m/s², added to CTG-PID."],
              ["Policy", "Tabular Q-learning; 6,000 training episodes; seed 17; α=0.12; γ=0.985; epsilon declines from 1.0 to 0.05 over the first 80%."],
              ["Reward", "Penalizes normalized gap error, relative speed, acceleration and jerk; also penalizes negative braking-distance margin and collision. Weights are in src/train_q_learning.py."],
              ["Fallback", "Tied/unvisited values choose the zero residual. This keeps the nominal controller active for unseen state bins, but does not guarantee safe behavior near learned bins."],
          ], [34*mm, WIDTH-34*mm]),
          P("Baselines, reward and guard assumptions", "H2x"),
          P("The CTG-PID command is clip(resistance(v) + 0.10e + 0.85(v_lead − v_ego), −6, 2.5), where e is gap error and acceleration is in m/s². The MPC baseline evaluates 35 candidate commands over an 18-step (1.8 s) horizon with a constant-acceleration lead prediction; it is a compact educational baseline, not a reproduction of a published MPC solver.", "Bodyx"),
          callout("r = −0.65(e_next/20)² − 0.18(Δv/8)² − 0.018(a/4)² − 0.012(j/8)² − 0.35·min(5, max(0, −margin)/5) − 120·I[collision]"),
          P("The guard assumes reaction time 0.35 s, ego braking capability 6 m/s², lead braking 8 m/s² and a 5 m standstill buffer. It selects the least-braking command that gives a nonnegative computed margin; when even maximum braking fails the calculation, it commands −6 m/s². These are fixed model assumptions, not measurements of a real vehicle.", "Smallx"),
          P("Evaluation measures", "H2x"),
          bullet("Gap RMSE (m): lower means closer average tracking to the chosen time-gap policy, not higher safety by itself."),
          bullet("Mean absolute jerk (m/s³): a rough longitudinal smoothness indicator. It does not capture every comfort factor."),
          bullet("Minimum TTC (s) and percent of closing-time samples below 2 s: conflict-surrogate indicators that depend on how TTC is defined."),
          bullet("Minimum gap (m) and simulated collisions: outcomes within this model and chosen scenarios only."),
          bullet("Guard interventions: count and percentage of time steps where the filter changes the proposed command."),
          bullet("Pulse amplification ratio: last follower's peak speed deviation divided by the leader's peak deviation in one selected four-vehicle test."),
          PageBreak()]

    s += [P("4. Literature synthesis — classical control and traffic response", "H1x"),
          P("String stability explains why ACC is more than a single-car tracking problem. A controller can maintain its own spacing and still amplify a braking disturbance down a vehicle string. Classical feedback and MPC methods provide interpretable baselines and a useful way to define measurable objectives.", "Bodyx"),
          P("Foundational and ACC-specific evidence", "H2x"),
          grid_table([
              ["Source", "Method and evidence", "Critical reading for this project"],
              ["Swaroop & Hedrick (1996)", "Formal analysis of string stability for interconnected systems; establishes conditions under which disturbances do not grow along a chain.", "Theory is valuable, but a finite simulation with one pulse is not a proof of string stability. Our four-car ratio is only a diagnostic."],
              ["Bageshwar, Garrard & Rajamani (2004)", "MPC for transitional ACC maneuvers; controller predicts traffic evolution to coordinate tracking and transients.", "Supports MPC as a meaningful comparator. Our small grid-search controller is much simpler than a research-grade MPC."],
              ["Li, Li, Rajamani & Wang (2011)", "Hierarchical multi-objective MPC for vehicular ACC; evaluates tracking, fuel-related objectives and driver response in heavy-duty-truck simulation.", "Shows that ACC objectives are coupled. Do not call this field validation or imply our passenger-car point-mass model replicates it."],
              ["Ploeg et al. (2014)", "Controller synthesis for string-stable CACC under communication topology and delay considerations.", "Useful platoon context, but it studies cooperative ACC with communication, unlike our nonconnected single-leader follower."],
              ["He et al. (2019) review", "Reviews ACC strategies implemented on experimental vehicles and outlines a layered development/evaluation view.", "Highlights the gap between simulation papers and experimental vehicles; real-world control details and field evidence are comparatively scarce."],
              ["Yu & Wang (2022) review", "State-of-the-art overview of ACC system research, algorithms and development directions.", "Use it to map the field, then cite primary studies for specific numerical findings."],
          ], [38*mm, 70*mm, WIDTH-108*mm], padd=4),
          P("Synthesis", "H2x"),
          P("Classical feedback and MPC are appropriate baselines because the spacing objective and vehicle model can be written explicitly. MPC's predictive structure can reduce tracking error, but depends on its prediction model, objective weights and computation. String stability is a separate question from a low single-vehicle RMSE. Review papers are useful for taxonomy; primary studies are needed when reporting specific controller results.", "Bodyx"),
          P("Automotive interpretation", "H2x"),
          callout("A useful ACC evaluation must report more than one number: tracking, smoothness, safety surrogates, disturbance propagation, operating assumptions and validation level."),
          PageBreak()]

    s += [P("5. Literature synthesis — reinforcement learning for following", "H1x"),
          P("RL is attractive where a hand-designed objective is hard to optimize across changing traffic patterns. It also brings data coverage, reward design, exploration and generalization problems. In car-following, the word “RL” covers very different targets: cooperation in a platoon, human-trajectory imitation, network-level traffic flow, or one vehicle's speed/gap control.", "Bodyx"),
          grid_table([
              ["Source", "Task / method / evidence", "What transfers—and what does not"],
              ["Watkins & Dayan (1992)", "Q-learning and convergence analysis for tabular Markov decision processes under its assumptions.", "Foundational algorithm reference. Convergence conditions do not establish good performance in a discretized, continuous, safety-critical vehicle task."],
              ["Desjardins & Chaib-draa (2011)", "Multi-agent RL for Cooperative Adaptive Cruise Control; focuses on vehicles acting cooperatively in a platoon.", "Shows an early connection between RL and cooperative ACC. Its communications and multi-agent setup differ from our nonconnected single-car task."],
              ["Zhu, Wang & Wang (2018)", "DDPG-based human-like car-following model trained/validated against naturalistic Chinese car-following trajectories; models reaction delay and trajectory behavior.", "Naturalistic data improves behavioral grounding. Reproducing human following is not the same as proving safe or optimal ACC."],
              ["Kreidieh, Wu & Bayen (2018)", "Deep RL control in traffic-flow simulations to dissipate stop-and-go waves; reports large wave reduction in selected network settings, including low CAV penetration cases.", "System-level flow benefits do not directly predict one-car gap tracking or emergency-braking safety."],
              ["Chu & Kalabic (2019)", "Model-based deep RL for CACC in mixed-autonomy vehicle platoons.", "Relevant to model-based learning and cooperation. Keep its platoon/CACC framing distinct from classical single-vehicle ACC."],
              ["Zhu et al. (2020)", "RL-based velocity control targeting safety, efficiency and comfort; evaluates car-following data/simulation and surrogate measures such as TTC and jerk.", "Reported reductions in dangerous-TTC exposure are dataset/simulation findings, not crash reductions or formal safety guarantees."],
              ["Lin, McPhee & Azad (2021)", "Compares DDPG with IPO-based MPC for ACC on a first-order control-oriented model. Reports comparable behavior in the training range with adequate MPC horizon; DRL episode cost is 5.8% above the full-episode IPO reference and out-of-range generalization degrades.", "The 5.8% is not a universal percentage “worse than MPC.” This study motivates explicit in-range and holdout testing."],
          ], [36*mm, 72*mm, WIDTH-108*mm], padd=4),
          P("Synthesis", "H2x"),
          P("The strongest design lesson is to compare like with like. Human trajectory reproduction, network traffic-wave damping and single-car ACC control have different state spaces, objectives and evidence. Many recent methods use deep function approximation; this project instead uses a small inspectable Q-table so that the learned action can be inspected and run without a deep-learning framework. That choice sacrifices continuous-state resolution and may limit performance.", "Bodyx"),
          PageBreak()]

    s += [P("6. Literature synthesis — safety and evaluation", "H1x"),
          grid_table([
              ["Source", "Contribution", "Boundary for our interpretation"],
              ["Ames et al. (2014)", "Control Barrier Function-QP formulation with a direct Adaptive Cruise Control application.", "A rigorous safety-filter reference. Our RSS-inspired stopping-distance calculation is not their CBF-QP and has no corresponding proof."],
              ["Shalev-Shwartz et al. (2017)", "Responsibility-Sensitive Safety safe-distance model, expressed through interpretable responsibility rules and braking assumptions.", "RSS is a formal model/approach; this prototype borrows a braking-margin idea but is not a full RSS implementation or a certified RSS controller."],
              ["Alshiekh et al. (2018)", "Shielding framework that filters actions to enforce temporal-logic safety specifications in modeled environments.", "A shield's assurance depends on the specification and model. Our filter is a numerical heuristic with explicit assumptions, not a formal shield."],
              ["Hailemichael et al. (2022)", "Safety filtering for RL-based ACC, including vehicle inertia and actuator saturation considerations.", "Directly relevant to the architecture. A paper's filter assumptions and guarantees must be read before transferring them to another vehicle model."],
              ["ElSamadisy et al. (2024)", "RL car-following with an analytic safety guarantee and dynamic target speed under the paper's formal model.", "Good example of formal assumptions alongside a learned controller. The guarantee is not inherited by this course project."],
              ["Vogel (2003)", "Compares headway and time-to-collision as traffic safety indicators.", "TTC is a surrogate, not a collision probability. Its interpretation changes with closing-speed definitions and nonclosing cases."],
              ["ISO 15622:2018", "Standard scope includes ACC control strategy, functionality, driver interface, diagnostics/failure reaction and performance test procedures.", "It is a useful vocabulary/checklist reference; the classroom simulation is not tested for conformity. ISO/DIS 15622 is also in development."],
              ["ISO 21448:2022", "SOTIF framework for unreasonable risk from functional insufficiencies and performance limitations.", "SOTIF is a lifecycle/argument framework, not a certificate created by adding a simple filter."],
          ], [34*mm, 66*mm, WIDTH-100*mm], padd=4),
          P("Safety-language checklist", "H2x"),
          bullet("Say: “The RSS-inspired filter maintained a nonnegative margin according to this simplified point-mass rule in the evaluated runs.”"),
          bullet("Avoid: “The vehicle is safe,” “the controller is collision-proof,” or “we implemented RSS/CBF/ISO compliance.”"),
          bullet("Say: “No simulated collisions occurred in the 1,000 expanded evaluation episodes under these model assumptions.”"),
          bullet("Avoid: “The model proves collision avoidance.” Zero observed collisions is not a formal guarantee and the tested sample is small."),
          PageBreak()]

    s += [P("7. Research gap and project contribution", "H1x"),
          P("The papers reviewed show mature work on ACC/MPC, strong interest in DRL car-following and several distinct strands of safe RL. Those results should not be collapsed into a single claim that “RL is better.” They vary by objective, network scale, dataset, model, baseline and evidence type.", "Bodyx"),
          P("Narrow gap addressed here", "H2x"),
          callout("For an automotive-technology project, can a small, inspectable, non-deep RL policy be integrated as a bounded residual around a conventional ACC controller, and can its trade-offs be evaluated against transparent baselines on both training-like and deliberately held-out scripted scenarios?"),
          P("Own work", "H2x"),
          bullet("A compact longitudinal vehicle model with drag, rolling resistance, actuator lag and bounded acceleration."),
          bullet("A tabular Q-learning policy that adds one of seven discrete residual accelerations to CTG-PID, with zero-residual tie/unvisited-state fallback."),
          bullet("A simplified one-move MPC and CTG-PID for matched baseline comparisons."),
          bullet("An RSS-inspired stopping-distance guard tested as an ablation around the Q policy."),
          bullet("A pre-run prediction sheet, a documented absolute-action pilot failure, a revised residual-Q design and a 50-seed matched comparison."),
          bullet("A four-car, single-pulse disturbance diagnostic and an annotated video of the simulated braking sequence."),
          P("Why keep the failed pilot?", "H2x"),
          P("The initial absolute-action Q table performed poorly: in-distribution gap RMSE was 15.20 m versus 2.36 m for CTG-PID and 1.58 m for MPC, with one collision in 24 in-distribution episodes. Its selected four-car pulse amplified speed deviation by 5.70×. The filter removed collisions in that small pilot but RMSE rose to 20.09 m. We retained those files and recorded why the action design changed; the revised residual-Q metrics are reported separately. This is evidence of iteration, not a result to hide.", "Bodyx"),
          PageBreak()]

    s += [P("8. Experimental method", "H1x"),
          grid_table([
              ["Element", "Protocol"],
              ["Training", "6,000 episodes, seed 17; randomized initial states and steady, smooth-wave and moderate-braking profiles."],
              ["Common-profile evaluation", "Steady, wave and moderate brake; 50 matched seeds for each profile and controller."],
              ["Held-out evaluation", "Randomized synthetic cut-in and higher-speed emergency braking; both families are excluded from Q training; 50 seeds per cell."],
              ["Controllers", "CTG-PID; one-move grid-search MPC; residual Q-learning; residual Q-learning + RSS-inspired guard."],
              ["Total evaluation", "5 scenario families × 4 controllers × 50 seeds = 1,000 episodes. Each runs up to 40 s at 0.1 s per step."],
              ["Matching", "Each seed has one fixed initial state and event; all four controllers receive the same version of that seed."],
              ["Intervals", "Episode means, sample SDs and approximate 95% normal intervals; paired intervals use per-seed controller differences. Descriptive only, not significance tests."],
          ], [44*mm, WIDTH-44*mm]),
          P("Scenario definitions", "H2x"),
          grid_table([
              ["Scenario", "Lead / ego event"],
              ["Steady", "Constant lead; base speed, ego speed and initial gap vary by seed."],
              ["Wave", "Smooth two-frequency speed variation; base speed, phase, ego speed and gap vary."],
              ["Brake", "Training-family moderate pulse: 3 m/s² for 3 s at 8 s, then hold and recover; base/gap vary."],
              ["Cut-in holdout", "Onset 6–10 s; gap drops 16–26 m instantaneously; lead brakes 3.5–5.0 m/s² for 2–3 s."],
              ["Emergency holdout", "Base speed 24–28 m/s; onset 5.5–9 s; 5.5–8.0 m/s² for 1.5–2.4 s."],
          ], [40*mm, WIDTH-40*mm], padd=4),
          P("Fair-comparison details worth explaining", "H2x"),
          bullet("Each run is reproducible from a seed, but the scripted seed ranges are not a statistical sample of natural driving or road tests."),
          bullet("The randomized holdouts check only the stated parameter ranges; they do not represent all out-of-distribution traffic."),
          bullet("The four controllers share a point-mass plant, but MPC uses a simplified constant-acceleration lead prediction and a short horizon."),
          bullet("The project reports approximate 95% intervals, not a hypothesis test. The paired intervals summarize per-seed differences."),
          bullet("The cut-in has an instantaneous gap discontinuity and no lateral dynamics, sensor delay or object-association uncertainty."),
          P("Reproducibility commands", "H2x"),
          callout("python -m venv .venv<br/>source .venv/bin/activate<br/>python -m pip install -r requirements.txt<br/>python src/train_q_learning.py --episodes 6000 --seed 17<br/>python src/run_experiments.py --seeds 50 --output outputs/formal_50seed<br/>python src/analyze_openacc.py<br/>python src/make_video.py --scenario cut_in --controller Q+RSS --trace outputs/formal_50seed/representative_traces.csv<br/>"),
          P("The MP4 script also needs ffmpeg installed on the computer. Source files and CSVs are included in the project folder.", "Smallx"),
          PageBreak()]

    s += [P("9. Measured results", "H1x"),
          P("Common-profile performance: mean across 150 episodes per controller (three profiles × 50 seeds)", "H2x"),
          grid_table([
              ["Controller", "Gap RMSE (m), mean ± SD", "Mean |jerk| (m/s³), mean ± SD", "TTC < 2 s"],
              ["CTG-PID", "2.46 ± 1.64", "0.216 ± 0.080", "0%"],
              ["MPC", "1.75 ± 1.26", "0.268 ± 0.069", "0%"],
              ["Residual Q", "3.24 ± 2.35", "0.505 ± 0.218", "0%"],
              ["Q + RSS-inspired guard", "3.24 ± 2.35", "0.505 ± 0.218", "0%"],
          ], [37*mm, 55*mm, 55*mm, WIDTH-147*mm]),
          P("Held-out performance: mean across 100 episodes per controller (two stress families × 50 seeds)", "H2x"),
          grid_table([
              ["Controller", "Gap RMSE (m), mean ± SD", "Mean |jerk| (m/s³), mean ± SD", "TTC < 2 s", "Guard edits / run"],
              ["CTG-PID", "3.58 ± 2.54", "0.282 ± 0.045", "0.20%", "0"],
              ["MPC", "2.36 ± 1.50", "0.579 ± 0.067", "0%", "0"],
              ["Residual Q", "4.77 ± 2.44", "0.738 ± 0.334", "1.02%", "0"],
              ["Q + RSS-inspired guard", "3.91 ± 1.67", "0.850 ± 0.451", "0%", "16.3 avg.; 4.08% of steps"],
          ], [37*mm, 43*mm, 47*mm, 33*mm, WIDTH-160*mm]),
          P("Read the tables carefully", "H2x"),
          bullet("The learner did not beat the baselines on aggregate tracking or jerk. MPC had the lowest RMSE in both groups; CTG-PID had lower mean absolute jerk than the RL variants."),
          bullet("Q and Q+guard match in common profiles because the guard made no changes in those 150 episodes."),
          bullet("Across the 100 held-out runs, Q+guard raised mean minimum gap from 13.40 m to 15.78 m and removed observed TTC<2 s exposure, while mean jerk rose from 0.738 to 0.850 m/s³."),
          bullet("No collision occurred in the 1,000 expanded episodes. This is an observation under this model and seed range, not a safety-rate estimate."),
          PageBreak()]

    s += [P("10. The critical cut-in and platoon findings", "H1x"),
          P("Randomized synthetic cut-in, 50 matched seeds per controller", "H2x"),
          grid_table([
              ["Controller", "Gap RMSE (m)", "Minimum TTC (s), episode mean", "Time below 2 s", "Minimum gap (m)", "Guard changes / episode"],
              ["CTG-PID", "5.98", "3.31", "0.40%", "8.58", "0"],
              ["MPC", "3.76", "19.42", "0%", "13.11", "0"],
              ["Residual Q", "6.96", "2.90", "2.04%", "7.00", "0"],
              ["Q + RSS-inspired guard", "5.40", "9.71", "0%", "11.35", "25.8 (6.46% of steps)"],
          ], [33*mm, 29*mm, 40*mm, 28*mm, 28*mm, WIDTH-158*mm]),
          P("The guard improved Q's minimum gap and short-TTC exposure over 50 matched seeds. MPC remained stronger on gap tracking and average minimum gap. TTC below 2 s is the share of closing samples in each run, averaged across runs; it is not a per-episode crash probability. The high MPC mean minimum TTC reflects each episode's closing pattern and should not be read as a safety probability.", "Bodyx"),
          P("Paired change from adding the guard to Q", "H2x"),
          grid_table([
              ["Measure (Q+guard minus Q)", "Mean paired change", "Approx. 95% interval", "Direction"],
              ["Minimum gap", "+4.355 m", "+4.026 to +4.683 m", "larger gap"],
              ["TTC<2 exposure", "−2.037 percentage points", "−3.138 to −0.936 points", "less exposure"],
              ["Mean absolute jerk", "+0.265 m/s³", "+0.239 to +0.290 m/s³", "rougher"],
              ["Gap RMSE", "−1.553 m", "−1.707 to −1.399 m", "closer than Q"],
          ], [48*mm, 40*mm, 47*mm, WIDTH-135*mm]),
          P("These intervals use matched per-seed differences and a normal approximation. They are descriptive summaries, not tests of statistical significance and not road-risk estimates.", "Smallx"),
          P("Four-car pulse diagnostic", "H2x"),
          grid_table([
              ["Controller", "Leader peak deviation (m/s)", "Last-follower peak (m/s)", "Amplification ratio"],
              ["CTG-PID", "2.40", "1.76", "0.735"],
              ["MPC", "2.40", "1.52", "0.633"],
              ["Residual Q", "2.40", "2.49", "1.040"],
              ["Q + RSS-inspired guard", "2.40", "2.49", "1.040"],
          ], [42*mm, 49*mm, 46*mm, WIDTH-137*mm]),
          P("The Q policy slightly amplified this selected speed pulse, while CTG-PID and MPC attenuated it. The RSS guard did not intervene in that particular platoon simulation. This is not a proof that a controller is or is not string-stable for every frequency, initial spacing, delay or vehicle string.", "Bodyx"),
          P("What an examiner should hear", "H2x"),
          callout("Our project is not an RL victory claim. It demonstrates a transparent RL integration, a fair baseline comparison, a visible generalization weakness and a measurable safety-filter trade-off. The principal result is that classical controllers performed better for this compact setup."),
          PageBreak()]

    s += [P("11. Discussion, limitations and next experiment", "H1x"),
          P("Interpretation", "H2x"),
          P("Residual Q-learning stayed much closer to the classical baseline than the failed absolute-action pilot, but its discrete corrections introduced oscillation and higher jerk. In the holdout cut-in, nearby learned bins could still select a poor correction; zero-residual fallback only protects ties/unvisited states. The guard improved selected risk surrogates by clipping commands according to a fixed braking model, but it did not reduce jerk, guarantee safe behavior under model error or establish a formal safety property.", "Bodyx"),
          P("Limitations to state out loud", "H2x"),
          bullet("One scripted leader, point-mass ego and deterministic dynamics; no sensor/perception errors, tire-road uncertainty or hardware."),
          bullet("Fifty seeds per scenario-controller pair and approximate intervals improve precision, but there is no hypothesis test or broad real-world uncertainty sweep."),
          bullet("The holdout scenarios are custom deterministic stress tests, not real-world distribution shift."),
          bullet("The CTG controller and one-move MPC are educational baselines, not tuned production or literature-replication implementations."),
          bullet("The reward weights, bins and fallback create a design choice; another discretization or learning schedule may change outcomes."),
          bullet("TTC, spacing error and pulse ratio are surrogate/diagnostic metrics. None is an ISO conformity assessment or crash-risk estimate."),
          bullet("The RSS-inspired filter assumes known gap/speed and fixed braking/reaction values; sensing error, actuator saturation, road friction and model mismatch are not proven safe."),
          P("Best next experiments", "H2x"),
          grid_table([
              ["Extension", "Question it would answer"],
              ["Replay annotated real cut-ins", "Do the differences remain when lead speed and gap come from a real lane-change trajectory?"],
              ["Ablate reward terms and state bins", "Which design choices cause jerk, tracking error or sparse state coverage?"],
              ["Parameter and sensor uncertainty", "How sensitive are the policy and guard to delay, mass, braking capability and gap error?"],
              ["CBF-QP or a formally specified shield", "Can an explicit safety condition be enforced with assumptions that can be reviewed?"],
              ["Fit a documented commercial ACC model", "Can an external controller reproduce public field headway and response traces?"],
              ["Hardware-in-the-loop, then controlled vehicle testing", "What changes when actuator and sensor timing are real? This requires safety supervision and approval."],
          ], [52*mm, WIDTH-52*mm]),
          PageBreak()]

    s += [P("12. Recommended written report structure", "H1x"),
          grid_table([
              ["Section", "What to include", "Evidence / common mistake"],
              ["Abstract", "Problem, objective, method, key measured result, limitation.", "Keep numbers aligned to the formal run; do not say the RL policy won."],
              ["Introduction", "ACC role, automotive motivation, problem, research question, contribution and scope.", "Avoid unverified market statistics and generic “AI is the future” claims."],
              ["Literature review", "Thematic synthesis of classical ACC/MPC, RL car-following and safety filtering.", "Compare task, data/model, baseline, result and limitation; do not list abstracts."],
              ["Method", "Vehicle model, CTG baseline, MPC, MDP, reward, training, filter, scenarios, seeds and metrics.", "Define the cut-in exactly; state the model is simulated and simplified."],
              ["Results", "Matched tables/plots, scenario-level cut-in, in-distribution/holdout summary and string diagnostic.", "Show units, episode counts and mean ± SD; do not omit bad results."],
              ["Discussion", "Answer each research question and explain tracking/comfort/safety trade-offs.", "A short TTC event is not a crash; no collision is not a guarantee."],
              ["Limitations / future work", "Model, data, randomization, sample size and assurance gaps; ordered next experiments.", "Make future steps concrete and tied to a limitation."],
              ["Conclusion", "One paragraph answering the question with the strongest evidence and boundary.", "Do not make claims outside the tested conditions."],
              ["References / appendix", "Consistent citations, parameter table, paper matrix, extra plots and project instructions.", "Every claim in the report must map to a traceable source or your own output."],
          ], [35*mm, 78*mm, WIDTH-113*mm], padd=4),
          P("Suggested literature-review paragraph structure", "H2x"),
          callout("Topic sentence → compare at least two sources → explain differences in task/data/baseline → identify the shared result or disagreement → state limitation → connect to the project question."),
          P("Example", "H2x"),
          P("“Classical ACC work commonly formulates following as a feedback or predictive-control problem. Bageshwar et al. (2004) study predictive control through transitional maneuvers, while Li et al. (2011) make the objective explicitly multi-objective and evaluate heavy-duty truck simulations. These studies motivate MPC as a baseline but do not establish how a small learned residual behaves on our point-mass passenger-car model. We therefore compare a compact MPC implementation against a transparent tabular policy under the same scripted trajectories.”", "QuoteX"),
          PageBreak()]

    s += [P("13. Research-paper analysis worksheet", "H1x"),
          P("Fill one copy for every paper selected for the final review. This sheet forces the review to separate source claims from your interpretation.", "Bodyx"),
          grid_table([
              ["Prompt", "Notes to complete"],
              ["Full citation and DOI / stable URL", "Author(s), year, exact title, venue, pages/article number, DOI."],
              ["Research question", "What engineering question is the paper actually answering?"],
              ["ACC problem class", "Single-car ACC, CACC/platoon, human behavior, network flow, safety filter, or general method?"],
              ["Evidence type", "Theory/proof; offline data; simulator; hardware-in-the-loop; experimental vehicle; review."],
              ["Model, data and assumptions", "Vehicle model, source data, lead profile, sensing/communication, reaction/actuator assumptions."],
              ["Method and baseline", "Controller/algorithm, comparison method, parameter tuning and any ablation."],
              ["Metrics and units", "Tracking error, jerk, fuel/energy, TTC/headway, collision/constraint events, string stability, runtime."],
              ["Main result", "Quote or paraphrase exact result with scenario/sample/model context."],
              ["Authors’ limitation", "What do the authors acknowledge?"],
              ["Your critique", "What is not controlled, generalized, measured or independently validated?"],
              ["Relevance to our project", "Which design decision, baseline, metric, scenario or caveat does this source inform?"],
              ["Confidence", "High: full paper and tables checked; medium: paper/author record; low: abstract only. Explain."],
          ], [47*mm, WIDTH-47*mm]),
          P("Quality-control questions", "H2x"),
          bullet("Did I verify the title, year, venue and DOI from a publisher, author or standards record?"),
          bullet("Did I distinguish simulation from naturalistic data and from real vehicle testing?"),
          bullet("Did I report the exact baseline and metric denominator?"),
          bullet("Did I keep an author's result separate from my own conclusion?"),
          bullet("Could a reader follow my statement to the source page, section, figure or table?"),
          PageBreak()]

    s += [P("14. Presentation talk track", "H1x"),
          P("A clean 16-slide, approximately 7–9 minute talk can follow this order. The PowerPoint includes editable speaker notes with citations. Replace the names placeholder, rehearse timing, and keep the research caveats visible.", "Bodyx"),
          grid_table([
              ["Slide", "What to say"],
              ["1 · Title", "We focused the ACC project on a cut-in response and evaluated it over 1,000 matched simulation episodes."],
              ["2 · Cut-in problem", "A new lead appears close; ACC must reduce closing speed without a harsh lurch. Our gap step is an approximation, not a lane-change model."],
              ["3 · Literature", "Classical control, RL car-following and safety filtering answer different questions. We use them to define a narrow, testable gap."],
              ["4 · Design / rubric", "The course awards literature review, own findings and actual research separately; our question focuses on the cut-in trade-off."],
              ["5 · Architecture", "A small Q table adds a bounded residual to CTG-PID. The braking-distance guard can clip a proposed command."],
              ["6 · Model", "The 10 Hz point-mass model keeps the experiment explainable; its binned state and discrete actions are coarse."],
              ["7 · Evaluation", "We use 50 matched seeds in each of five scenario families and four controllers. Cut-in onset, gap drop and lead braking vary by seed."],
              ["8 · Tracking", "MPC has the lowest group mean gap RMSE: 1.75 m on common profiles and 2.36 m on held-out stresses."],
              ["9 · Comfort", "The guard improved Q's cut-in risk surrogates, but mean absolute jerk rose from 0.957 to 1.222 m/s³."],
              ["10 · Cut-in metrics", "Across 50 runs, Q+guard raised mean minimum gap from 7.00 to 11.35 m and reduced TTC<2 exposure from 2.04% to zero."],
              ["11 · Trajectory", "This is one matched example. The aggregate chart above uses all 50 randomized cut-in seeds."],
              ["12 · Production ACC", "A 2025 Honda manual documents interval settings and a cut-in warning; one public OpenACC run gives a real headway reference, not a controller benchmark."],
              ["13 · Own work", "The absolute-action Q pilot failed. The residual redesign kept CTG in charge, yet did not beat CTG or MPC."],
              ["14 · Takeaway", "The guard is better than unguarded Q on this stress, but not better than MPC or a current commercial ACC overall."],
              ["15–16 · References", "These primary studies, official dataset pages, current owner manual and standards pages anchor the claims."],
          ], [35*mm, WIDTH-35*mm]),
          PageBreak()]

    s += [P("15. Viva questions and defensible answers", "H1x"),
          grid_table([
              ["Question", "Answer to practice"],
              ["Why adaptive cruise control?", "It is directly automotive: longitudinal vehicle dynamics, following distance, acceleration, comfort, braking and traffic response. It supports a simulation-focused project without needing a full autonomous-driving stack."],
              ["Why not use deep RL?", "We chose tabular Q-learning to keep state/action values inspectable and avoid a heavy deep-learning runtime. The trade-off is coarse discretization and limited state coverage."],
              ["What exactly is learned?", "A discrete acceleration residual added to CTG-PID. The base controller remains responsible for nominal tracking."],
              ["Why did you choose residual RL?", "The first absolute-action pilot was unstable and had very poor tracking; the residual structure bounds the learned contribution around a known baseline."],
              ["Did RL beat MPC?", "No. MPC had lower group RMSE and the largest mean minimum gap in the cut-in family. Q+guard improved Q on two selected cut-in indicators only."],
              ["What does 2.04% TTC-below-2 mean?", "It is the mean per-episode share of closing samples below 2 s for Q over 50 randomized cut-in runs. It is not a crash probability."],
              ["Did the guard make the system safe?", "No. It improved selected surrogate indicators under a simplified braking-margin rule. It is not formal RSS/CBF, and its assumptions and sensing/model errors are not validated."],
              ["Why did Q+guard equal Q in-distribution?", "The guard made zero interventions in those tested runs, so its output matched the learned command."],
              ["Why does the guard increase jerk?", "Clipping can create sharper command changes. Here it also changes tracking and actions frequently during the cut-in; a smoothness-aware filter is a next step."],
              ["How many papers does the rubric require?", "The attached guide assigns 30–35 marks to the literature review and suggests about 13 relevant papers. The 30–35 figure is a mark range, not a paper count."],
              ["What is string stability?", "A disturbance should not grow as it propagates down a vehicle string. Our ratio tests one four-car disturbance and cannot prove the property generally."],
              ["What is the most important limitation?", "The cut-in changes gap instantaneously and has no lane geometry or perception model. We also lack a commercial controller run under the same cut-in."],
              ["What would you improve first?", "Replay a hand-annotated real cut-in in a vehicle-calibrated model with sensor delay, then measure the product or public-data baseline under comparable conditions."],
              ["Can this be used in a car?", "No. It is a course simulation and not designed, validated or certified for road use."],
          ], [56*mm, WIDTH-56*mm], padd=4),
          PageBreak()]

    s += [P("16. References", "H1x"),
          P("Core sources for the literature review", "H2x")]
    refs = [
        ("Ames, A. D., Xu, X., Grizzle, J. W., & Tabuada, P. (2014). Control barrier function based quadratic programs with application to adaptive cruise control. IEEE Conference on Decision and Control. ", "10.1109/CDC.2014.7040372"),
        ("Alshiekh, M., Bloem, R., Ehlers, R., Könighofer, B., Niekum, S., & Topcu, U. (2018). Safe reinforcement learning via shielding. Proceedings of AAAI, 32(1), 2669–2678. ", "10.1609/AAAI.V32I1.11797"),
        ("Bageshwar, V. L., Garrard, W. L., & Rajamani, R. (2004). Model predictive control of transitional maneuvers for adaptive cruise control vehicles. IEEE Transactions on Vehicular Technology, 53(5), 1573–1585. ", "10.1109/TVT.2004.833625"),
        ("Chu, T., & Kalabic, U. (2019). Model-based deep reinforcement learning for CACC in mixed-autonomy vehicle platoons. IEEE Conference on Decision and Control. ", "10.1109/CDC40024.2019.9030110"),
        ("Desjardins, C., & Chaib-draa, B. (2011). Cooperative adaptive cruise control: A reinforcement learning approach. IEEE Transactions on Intelligent Transportation Systems, 12(4), 1248–1260. ", "10.1109/TITS.2011.2157145"),
        ("ElSamadisy, M., et al. (2024). Safe, efficient, and comfortable reinforcement-learning-based car-following for AVs with an analytic safety guarantee and dynamic target speed. Transportation Research Record, 2678(1), 643–661. ", "10.1177/03611981231171899"),
        ("Hailemichael, G., Ayalew, B., Kerbel, G., Ivanco, A., & Loiselle, J. (2022). Safety filtering for reinforcement learning-based adaptive cruise control. IFAC-PapersOnLine, 55(24). ", "10.1016/j.ifacol.2022.10.276"),
        ("He, Y., Ciuffo, B., Zhou, Q., Makridis, M., Mattas, K., Li, J., Li, Z., Yan, F., & Xu, H. (2019). Adaptive cruise control strategies implemented on experimental vehicles: A review. IFAC-PapersOnLine, 52(5), 21–27. ", "10.1016/j.ifacol.2019.09.004"),
        ("Kreidieh, A. R., Wu, C., & Bayen, A. M. (2018). Dissipating stop-and-go waves in closed and open networks via deep reinforcement learning. IEEE International Conference on Intelligent Transportation Systems, 1475–1480. ", "10.1109/ITSC.2018.8569485"),
        ("Li, S. E., Li, K., Rajamani, R., & Wang, J. (2011). Model predictive multi-objective vehicular adaptive cruise control. IEEE Transactions on Control Systems Technology, 19(3), 556–566. ", "10.1109/TCST.2010.2049203"),
        ("Lin, Y., McPhee, J., & Azad, N. L. (2021). Comparison of deep reinforcement learning and model predictive control for adaptive cruise control. IEEE Transactions on Intelligent Vehicles, 6, 221–231. ", "10.1109/TIV.2020.3012947"),
        ("Makridis, M., Mattas, K., Anesiadou, A., & Ciuffo, B. (2021). OpenACC: An open database of car-following experiments to study the properties of commercial ACC systems. Transportation Research Part C, 125, 103047. ", "10.1016/j.trc.2021.103047"),
        ("Ploeg, J., van de Wouw, N., & Nijmeijer, H. (2014). Controller synthesis for string stability of vehicle platoons. IEEE Transactions on Intelligent Transportation Systems, 15(2), 854–865. ", "10.1109/TITS.2013.2291493"),
        ("Shalev-Shwartz, S., Shammah, S., & Shashua, A. (2017). On a formal model of safe and scalable self-driving cars. arXiv:1708.06374. ", "arXiv:1708.06374"),
        ("Swaroop, D., & Hedrick, J. K. (1996). String stability of interconnected systems. IEEE Transactions on Automatic Control, 41(3), 349–357. ", "10.1109/9.486636"),
        ("Vogel, K. (2003). A comparison of headway and time to collision as safety indicators. Accident Analysis & Prevention, 35(3), 427–433. ", "10.1016/S0001-4575(02)00022-2"),
        ("Watkins, C. J. C. H., & Dayan, P. (1992). Q-learning. Machine Learning, 8, 279–292. ", "10.1007/BF00992698"),
        ("Yu, S., & Wang, J. (2022). Researches on adaptive cruise control system: A state of the art review. Proceedings of the Institution of Mechanical Engineers, Part D: Journal of Automobile Engineering, 236(2–3), 211–240. ", "10.1177/09544070211019254"),
        ("Zhu, M., Wang, X., & Wang, Y. (2018). Human-like autonomous car-following model with deep reinforcement learning. Transportation Research Part C, 97, 348–368. ", "10.1016/j.trc.2018.10.024"),
        ("Zhu, M., Wang, Y., Pu, Z., Hu, J., Wang, X., & Ke, R. (2020). Safe, efficient, and comfortable velocity control based on reinforcement learning for autonomous driving. Transportation Research Part C, 117, 102662. ", "10.1016/j.trc.2020.102662"),
    ]
    for text, doi_value in refs:
        if doi_value.startswith("arXiv"):
            url = "https://arxiv.org/abs/1708.06374"
            citation = text + link(doi_value, url)
        else:
            citation = text + doi(doi_value)
        s.append(P(citation, "Ref"))
    s += [P("Standards and project material", "H2x"),
          P("International Organization for Standardization. ISO 15622:2018, Intelligent transport systems — Adaptive cruise control systems — Performance requirements and test procedures. " + link("Official ISO record", "https://www.iso.org/standard/71515.html"), "Ref"),
          P("International Organization for Standardization. ISO 21448:2022, Road vehicles — Safety of the intended functionality (SOTIF). " + link("Official ISO record", "https://www.iso.org/standard/77490.html"), "Ref"),
          P("Project code, model, training logs, OpenACC sample and analysis, experiment summaries, predictions, iteration log and simulation video are supplied alongside this handbook. Results refer to the expanded 16 October 2026 run.", "Smallx"),
          PageBreak()]

    s += [P("Appendix A · Claim discipline", "H1x"),
          grid_table([
              ["If you want to say…", "Use this version"],
              ["“The model is safe.”", "“No collision occurred in 1,000 simulated episodes. The guard removed observed TTC<2 s exposure in the randomized cut-in runs. Neither result is a safety proof.”"],
              ["“RL is better than MPC.”", "“In this setup, MPC had the lowest gap RMSE. The tabular residual Q policy was more transparent but less accurate and less smooth.”"],
              ["“The cut-in caused a lane change.”", "“The cut-in was represented by an instantaneous 16–26 m reduction in simulated gap; lateral lane dynamics were not modeled.”"],
              ["“We tested ISO 15622.”", "“We used ISO 15622 as a reference for ACC performance terminology; we did not run a conformity test.”"],
              ["“RSS filter.”", "“RSS-inspired braking-distance guard. This is a simplified project heuristic, not the full RSS model or its formal safety argument.”"],
              ["“The string-stability ratio proves stability.”", "“The last-follower peak was below/above the leader peak in one selected four-car pulse test.”"],
          ], [55*mm, WIDTH-55*mm]),
          P("Appendix B · Files to submit / present", "H2x"),
          bullet("Presentation with names inserted and notes reviewed."),
          bullet("This handbook PDF and a separately written report using the paper-analysis sheets."),
          bullet("Python project, trained table, fixed random seeds, CSV experiment outputs and run instructions."),
          bullet("Brake and/or cut-in MP4, with a verbal reminder that it shows simulated behavior."),
          bullet("A short appendix showing one selected paper matrix, reward/state/action definitions and exact result tables."),
          Spacer(1, 6*mm),
          callout("Keep the deliverables consistent: the same scenario names, numbers, units and limitations should appear in the slides, guide, report and oral explanation.", bg=PALE_BLUE, accent=NAVY)]
    return s


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=LEFT, rightMargin=RIGHT, topMargin=TOP, bottomMargin=BOTTOM, title="Reinforcement Learning for Adaptive Cruise Control — Project Guide", author="Automotive Technology Project")
    frame = Frame(LEFT, BOTTOM, WIDTH, PAGE_H - TOP - BOTTOM, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="main")
    doc.addPageTemplates([PageTemplate(id="project", frames=[frame], onPage=header_footer)])
    doc.build(build_story())
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
