import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const presentationToolsPath = '/Users/rajpratapsinghgurjar/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations/container_tools/artifact_tool_utils.mjs';
const { applyPresentationChartFont } = await import(pathToFileURL(presentationToolsPath).href);

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const outDir = path.join(root, 'output');
const buildDir = path.join(root, '.build');
const finalPath = path.join(outDir, 'ACC_RL_CutIn_Focused_Presentation.pptx');
const candidatePath = path.join(buildDir, 'ACC_RL_CutIn_Focused_Presentation_candidate.pptx');
const slideDir = path.join(buildDir, 'presentation_preview');
const W = 1280, H = 720;

function parseCsv(textValue) {
  const [header, ...lines] = textValue.trim().split(/\r?\n/);
  const fields = header.split(',');
  return lines.map(lineValue => {
    const values = lineValue.split(',');
    return Object.fromEntries(fields.map((field, index) => [field, values[index]]));
  });
}

const experimentManifest = JSON.parse(await fs.readFile(path.join(root, 'outputs/formal_50seed/experiment_manifest.json'), 'utf8'));
const representativeTraces = parseCsv(await fs.readFile(path.join(root, 'outputs/formal_50seed/representative_traces.csv'), 'utf8'));

const C = {
  navy: '#102437', ink: '#1D2E3B', muted: '#667A8A', paper: '#F6F8F9',
  white: '#FFFFFF', teal: '#0E9F94', tealDark: '#087C75', paleTeal: '#E7F4F2',
  blue: '#3F7990', amber: '#D98F32', paleAmber: '#FFF3E2', red: '#B94E45',
  rule: '#D8E1E7', dark2: '#1A3548', gray: '#93A3AE',
};

const presentation = Presentation.create({ slideSize: { width: W, height: H } });

function addShape(slide, geometry, x, y, w, h, fill = 'none', lineFill = 'none', lineWidth = 0, name = undefined, extra = {}) {
  return slide.shapes.add({
    geometry, name,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: 'solid', fill: lineFill, width: lineWidth },
    ...extra,
  });
}

function text(slide, value, x, y, w, h, opts = {}) {
  const sh = addShape(slide, 'textbox', x, y, w, h, opts.boxFill ?? 'none', opts.boxLine ?? 'none', opts.boxLineWidth ?? 0, opts.name);
  sh.text = value;
  sh.text.insets = opts.insets ?? 0;
  sh.text.style = {
    typeface: opts.font ?? 'Arial',
    fontSize: opts.size ?? 22,
    bold: opts.bold ?? false,
    color: opts.color ?? C.ink,
    alignment: opts.align ?? 'left',
  };
  return sh;
}

function line(slide, x1, y1, x2, y2, color = C.rule, width = 1) {
  return addShape(slide, 'line', x1, y1, x2 - x1, y2 - y1, 'none', color, width);
}

function baseSlide(section, title, slideNo, opts = {}) {
  const slide = presentation.slides.add();
  slide.background.fill = opts.dark ? C.navy : C.paper;
  if (opts.dark) {
    addShape(slide, 'rect', 0, 0, 12, H, C.teal);
    text(slide, section.toUpperCase(), 66, 48, 450, 26, { size: 14, bold: true, color: C.teal });
    text(slide, title, 66, 98, 1125, opts.titleH ?? 116, { size: opts.titleSize ?? 44, bold: true, color: C.white, name: `slide-${slideNo}-title` });
    text(slide, `${String(slideNo).padStart(2, '0')}   /   16`, 1090, 674, 128, 18, { size: 12, color: '#B8C6D0', align: 'right' });
  } else {
    addShape(slide, 'rect', 0, 0, 1280, 7, C.teal);
    text(slide, section.toUpperCase(), 58, 32, 450, 20, { size: 13, bold: true, color: C.tealDark });
    text(slide, title, 58, 65, 1164, opts.titleH ?? 72, { size: opts.titleSize ?? 34, bold: true, color: C.navy, name: `slide-${slideNo}-title` });
    line(slide, 58, 674, 1222, 674, C.rule, 1);
    text(slide, 'AUTOMOTIVE TECHNOLOGY  ·  ACC + RL', 58, 685, 500, 15, { size: 10.5, color: C.muted });
    text(slide, String(slideNo).padStart(2, '0'), 1180, 684, 42, 16, { size: 11, color: C.muted, align: 'right' });
  }
  return slide;
}

function bullets(slide, items, x, y, w, opts = {}) {
  const size = opts.size ?? 20, lineH = opts.lineH ?? 52;
  items.forEach((item, i) => {
    const yy = y + i * lineH;
    addShape(slide, 'ellipse', x, yy + 10, 8, 8, opts.dot ?? C.teal);
    text(slide, item, x + 22, yy, w - 22, lineH - 2, { size, color: opts.color ?? C.ink });
  });
}

function labelValue(slide, label, value, x, y, w, valueColor = C.navy) {
  text(slide, label.toUpperCase(), x, y, w, 20, { size: 12, bold: true, color: C.muted });
  text(slide, value, x, y + 27, w, 48, { size: 31, bold: true, color: valueColor });
}

function notes(slide, textValue) {
  slide.speakerNotes.text = textValue;
}

function addChart(slide, kind, cfg) {
  const chart = slide.charts.add(kind, {
    chartFill: C.paper,
    chartLine: { style: 'solid', fill: 'none', width: 0 },
    plotAreaFill: C.paper,
    plotAreaLine: { style: 'solid', fill: 'none', width: 0 },
    titleTextStyle: { fontSize: 18, bold: true, fill: C.navy },
    xAxis: { textStyle: { fill: C.muted, fontSize: 14 }, line: { style: 'solid', fill: C.rule, width: 1 }, majorGridlines: null },
    yAxis: { textStyle: { fill: C.muted, fontSize: 13 }, line: { style: 'solid', fill: C.rule, width: 1 }, majorGridlines: { style: 'solid', fill: C.rule, width: 1 } },
    ...cfg,
  });
  applyPresentationChartFont(chart, { fontFamily: 'Arial' });
  return chart;
}

// 1 — Cover
{
  const s = baseSlide('Course project', 'Can a small RL correction help ACC handle a sudden cut-in?', 1, { dark: true, titleSize: 50, titleH: 158 });
  text(s, 'A clear cut-in test against classical control and a real-world commercial ACC reference', 67, 279, 975, 65, { size: 24, color: '#D5E0E7' });
  addShape(s, 'rect', 67, 388, 70, 4, C.amber);
  text(s, 'Automotive technology project', 67, 416, 540, 30, { size: 18, bold: true, color: C.white });
  text(s, 'Team members: add names', 67, 459, 540, 28, { size: 16, color: '#B8C6D0' });
  text(s, '1,000 matched simulation episodes · one focused automotive challenge', 67, 612, 840, 25, { size: 16, color: '#B8C6D0' });
  notes(s, 'Opening: We asked whether a compact tabular Q-learning correction can help an ACC controller react to a sudden cut-in. We compare CTG-PID, a simplified MPC, residual Q and residual Q with a braking-distance guard over 1,000 matched episodes. A public commercial ACC field trace provides real-world context, but not a direct head-to-head cut-in test.');
}

// 2 — Automotive problem
{
  const s = baseSlide('01 · The niche', 'A car joins the lane. ACC must close the gap without a harsh lurch.', 2, { titleSize: 31 });
  text(s, 'A cut-in is interesting because the target changes suddenly while the ego car is already moving.', 58, 148, 695, 54, { size: 22, color: C.ink });
  // Simple editable road illustration.
  addShape(s, 'roundRect', 58, 235, 690, 282, C.navy, 'none', 0, 'cutin-road-panel', { borderRadius: 18 });
  line(s, 82, 375, 724, 375, '#7B8A96', 2);
  for (let x = 96; x < 700; x += 86) addShape(s, 'roundRect', x, 374, 42, 5, C.white, 'none', 0);
  addShape(s, 'roundRect', 206, 300, 132, 56, C.teal, C.white, 1, 'ego-car', { borderRadius: 12 });
  text(s, 'EGO', 238, 317, 80, 22, { size: 17, bold: true, color: C.white, align: 'center' });
  addShape(s, 'roundRect', 522, 300, 132, 56, C.amber, C.white, 1, 'lead-car', { borderRadius: 12 });
  text(s, 'NEW LEAD', 529, 317, 118, 22, { size: 16, bold: true, color: C.white, align: 'center' });
  line(s, 339, 330, 519, 330, C.white, 2);
  text(s, 'before: larger gap', 352, 283, 166, 20, { size: 14, color: '#CAD7DF', align: 'center' });
  addShape(s, 'rightArrow', 399, 408, 98, 38, C.amber, 'none', 0);
  text(s, 'gap suddenly shrinks', 349, 457, 198, 22, { size: 14, bold: true, color: C.white, align: 'center' });
  line(s, 795, 148, 795, 600, C.rule, 1.4);
  text(s, 'OUR CUT-IN STRESS', 836, 164, 342, 24, { size: 13, bold: true, color: C.amber });
  text(s, '16–26 m', 836, 203, 300, 47, { size: 34, bold: true, color: C.navy });
  text(s, 'instant gap drop, at a randomized time', 836, 253, 333, 37, { size: 16, color: C.muted });
  text(s, '3.5–5.0 m/s²', 836, 320, 310, 46, { size: 31, bold: true, color: C.navy });
  text(s, 'lead-vehicle braking for 2–3 s', 836, 369, 340, 36, { size: 16, color: C.muted });
  text(s, 'We measure', 836, 434, 230, 25, { size: 18, bold: true, color: C.tealDark });
  text(s, 'minimum gap · time-to-collision · jerk', 836, 469, 352, 62, { size: 17, color: C.ink });
  text(s, 'The simulator changes distance only; it does not simulate the lane change or perception.', 58, 578, 1115, 42, { size: 17, bold: true, color: C.tealDark });
  notes(s, 'Explain cut-in in everyday terms: a new lead vehicle appears closer than the one being followed. The chosen niche is the short response window: braking must reduce closing speed, but sudden commands can feel harsh. Across seeds, the model instantly drops the longitudinal gap by 16–26 m at 6–10 s, then the lead brakes 3.5–5.0 m/s² for 2–3 s. It does not draw a lane change, model radar perception, or claim that an actual commercial ACC system uses these exact maneuvers.');
}

// 3 — Evidence landscape
{
  const s = baseSlide('02 · Literature', 'Three research threads shape the question.', 3);
  const cols = [
    { x: 58, title: 'CLASSICAL ACC', accent: C.blue, body: 'Bageshwar et al. (2004)\nPredictive control for transitional maneuvers.\n\nLi et al. (2011)\nMulti-objective ACC MPC.\n\nHe et al. (2019)\nReview of experimental-vehicle strategies.', take: 'Strong baselines; real-vehicle evidence remains comparatively limited.' },
    { x: 452, title: 'LEARNED FOLLOWING', accent: C.tealDark, body: 'Desjardins & Chaib-draa (2011)\nRL for cooperative ACC.\n\nZhu et al. (2018, 2020)\nNaturalistic car-following and safety/comfort objectives.\n\nLin et al. (2021)\nDRL vs MPC for ACC.', take: 'Objectives and evidence settings vary across papers.' },
    { x: 846, title: 'SAFETY METHODS', accent: C.amber, body: 'Ames et al. (2014)\nCBF-QP applied to ACC.\n\nRSS (2017) · shielding (2018)\nExplicit safety rules / action filtering.\n\nHailemichael et al. (2022)\nSafety filtering for RL-based ACC.', take: 'Assurance depends on explicit models and assumptions.' },
  ];
  cols.forEach((c, i) => {
    if (i) line(s, c.x - 23, 156, c.x - 23, 601, C.rule, 1.25);
    text(s, c.title, c.x, 158, 340, 24, { size: 14, bold: true, color: c.accent });
    text(s, c.body, c.x, 204, 340, 255, { size: 18, color: C.ink });
    line(s, c.x, 478, c.x + 328, 478, C.rule, 1);
    text(s, c.take, c.x, 499, 330, 82, { size: 16, bold: true, color: C.navy });
  });
  notes(s, 'Synthesize by research question. Classical control papers study tracking and transitions; RL studies may reproduce human trajectories, coordinate vehicles, or optimize traffic flow; safety papers define different kinds of filters or formal conditions. Do not treat their results as directly interchangeable. References: Bageshwar et al. 2004, https://doi.org/10.1109/TVT.2004.833625; Li et al. 2011, https://doi.org/10.1109/TCST.2010.2049203; He et al. 2019, https://doi.org/10.1016/j.ifacol.2019.09.004; Desjardins & Chaib-draa 2011, https://doi.org/10.1109/TITS.2011.2157145; Zhu et al. 2018, https://doi.org/10.1016/j.trc.2018.10.024; Zhu et al. 2020, https://doi.org/10.1016/j.trc.2020.102662; Lin et al. 2021, https://doi.org/10.1109/TIV.2020.3012947; Ames et al. 2014, https://doi.org/10.1109/CDC.2014.7040372; Shalev-Shwartz et al. 2017, https://arxiv.org/abs/1708.06374; Alshiekh et al. 2018, https://doi.org/10.1609/AAAI.V32I1.11797; Hailemichael et al. 2022, https://doi.org/10.1016/j.ifacol.2022.10.276.');
}

// 4 — Research question
{
  const s = baseSlide('03 · Research design', 'Can tabular RL improve a CTG controller without hiding the control logic?', 4, { titleSize: 31 });
  text(s, 'We test a small learned acceleration residual, then compare it with CTG-PID and simplified MPC.', 58, 157, 660, 89, { size: 24, color: C.ink });
  text(s, 'RUBRIC NOTE', 58, 315, 210, 22, { size: 13, bold: true, color: C.amber });
  text(s, '30–35 marks', 58, 350, 295, 45, { size: 34, bold: true, color: C.navy });
  text(s, 'for the literature review', 58, 404, 320, 30, { size: 18, color: C.muted });
  text(s, '10 marks', 408, 350, 245, 45, { size: 34, bold: true, color: C.navy });
  text(s, 'for own work / findings', 408, 404, 300, 30, { size: 18, color: C.muted });
  text(s, '30–35 marks', 58, 461, 300, 42, { size: 30, bold: true, color: C.navy });
  text(s, 'for actual research', 58, 511, 310, 28, { size: 18, color: C.muted });
  line(s, 760, 158, 760, 596, C.rule, 1.5);
  text(s, '13', 824, 182, 140, 78, { size: 66, bold: true, color: C.teal });
  text(s, 'The supplied guide suggests about 13 papers.', 824, 267, 338, 61, { size: 22, bold: true, color: C.navy });
  text(s, 'The 30–35 figures are mark bands, not required paper counts.', 824, 368, 338, 82, { size: 19, color: C.ink });
  text(s, 'Project contribution: transparent residual Q + matched evaluation + honest limits.', 824, 492, 338, 85, { size: 18, bold: true, color: C.tealDark });
  notes(s, 'The attached course guide allocates 30–35 marks to the literature review, 10 to own work/findings, and 30–35 to actual research. It separately suggests about 13 papers. We interpreted the mark values correctly and designed a focused review rather than assuming the team needs 30–35 papers.');
}

// 5 — System diagram
{
  const s = baseSlide('04 · Architecture', 'The learned action is a small residual inside an automotive control loop.', 5, { titleSize: 31 });
  const blocks = [
    { x: 58, w: 175, title: 'Lead profile', sub: 'speed + braking\nscenario' },
    { x: 276, w: 190, title: 'Observation', sub: 'gap error · closing speed\nego speed · acceleration' },
    { x: 510, w: 185, title: 'CTG-PID', sub: 'nominal time-gap\nfeedback command' },
    { x: 739, w: 177, title: 'Q table', sub: 'discrete residual\nacceleration' },
    { x: 958, w: 176, title: 'Action guard', sub: 'RSS-inspired\nbraking margin' },
  ];
  blocks.forEach((b, i) => {
    addShape(s, 'roundRect', b.x, 248, b.w, 133, i === 4 ? C.paleAmber : (i === 3 ? C.paleTeal : C.white), C.rule, 1, `architecture-block-${i + 1}`, { borderRadius: 12 });
    text(s, b.title, b.x + 13, 271, b.w - 26, 30, { size: 20, bold: true, color: i === 4 ? C.amber : C.navy, align: 'center' });
    text(s, b.sub, b.x + 12, 315, b.w - 24, 53, { size: 15.5, color: C.muted, align: 'center' });
    if (i < blocks.length - 1) {
      addShape(s, 'rightArrow', b.x + b.w + 6, 295, 30, 24, C.gray, 'none', 0);
    }
  });
  addShape(s, 'roundRect', 487, 438, 477, 89, C.navy, 'none', 0, 'vehicle-plant', { borderRadius: 12 });
  text(s, 'Actuator + ego vehicle', 505, 455, 440, 29, { size: 22, bold: true, color: C.white, align: 'center' });
  text(s, 'first-order lag · drag · rolling resistance · bounded acceleration', 507, 490, 438, 22, { size: 14, color: '#CBD8E0', align: 'center' });
  addShape(s, 'rightArrow', 1019, 459, 34, 26, C.teal, 'none', 0);
  text(s, 'ego motion', 1058, 459, 150, 24, { size: 15, bold: true, color: C.tealDark });
  text(s, 'A zero residual leaves CTG-PID in charge for tied or unvisited state bins.', 58, 579, 1100, 35, { size: 18, color: C.ink });
  notes(s, 'Walk left to right. The lead profile sets speed; state features describe the car-following situation; CTG-PID supplies the nominal acceleration; Q chooses a discrete residual; an optional braking-distance guard can clip the command; actuator and longitudinal plant determine next state. In unseen or tied table states the action is zero residual. This fallback does not prove safety.');
}

// 6 — Model and MDP
{
  const s = baseSlide('05 · Model and policy', 'A compact model keeps the experiment inspectable.', 6);
  text(s, 'VEHICLE MODEL', 58, 160, 220, 21, { size: 13, bold: true, color: C.tealDark });
  text(s, 'Δt = 0.1 s  ·  mass = 1,500 kg\nactuator τ = 0.35 s\nacceleration command = −6 to +2.5 m/s²', 58, 197, 515, 100, { size: 22, color: C.navy });
  line(s, 613, 160, 613, 602, C.rule, 1.4);
  text(s, 'TIME-GAP POLICY', 656, 160, 260, 21, { size: 13, bold: true, color: C.tealDark });
  text(s, 'd* = 5 m + 1.3 v', 656, 203, 520, 55, { size: 38, bold: true, color: C.navy });
  text(s, 'Five state features', 58, 363, 255, 27, { size: 20, bold: true, color: C.ink });
  bullets(s, ['gap error', 'closing speed', 'ego speed', 'actual ego acceleration', 'estimated lead acceleration'], 58, 407, 490, { size: 16.5, lineH: 36 });
  text(s, 'Seven residual actions', 656, 363, 270, 27, { size: 20, bold: true, color: C.ink });
  text(s, '−1.2  −0.6  −0.25  0  +0.25  +0.6  +1.2 m/s²', 656, 406, 535, 36, { size: 20, bold: true, color: C.tealDark });
  text(s, '6,000 episodes  ·  α = 0.12  ·  γ = 0.985', 656, 476, 515, 32, { size: 18, color: C.muted });
  text(s, 'The reward penalizes gap error, relative speed, acceleration, jerk, negative braking margin and collision.', 656, 520, 530, 74, { size: 17, color: C.ink });
  notes(s, 'Describe the 10 Hz longitudinal point-mass model and the chosen time-gap policy. The Q-table has five discretized state features and seven acceleration residuals. The reward combines normalized tracking, relative-speed, acceleration and jerk penalties, a soft negative-margin shaping cost and a large collision penalty. The discretization is intentionally inspectable but many bins are never visited; the chosen action granularity is a limitation. Q-learning update follows Watkins and Dayan (1992), https://doi.org/10.1007/BF00992698.');
}

// 7 — Protocol
{
  const s = baseSlide('06 · Evaluation protocol', 'Five scenario families, 50 matched seeds each, four controllers.', 7, { titleSize: 30 });
  const leftX = 58;
  text(s, 'TRAINING', leftX, 155, 190, 21, { size: 13, bold: true, color: C.tealDark });
  text(s, '6,000 episodes', leftX, 190, 290, 43, { size: 30, bold: true, color: C.navy });
  text(s, 'steady · smooth wave · moderate brake', leftX, 241, 310, 52, { size: 17, color: C.muted });
  line(s, 420, 156, 420, 590, C.rule, 1.4);
  text(s, 'IN-DISTRIBUTION', 474, 155, 270, 21, { size: 13, bold: true, color: C.tealDark });
  text(s, '3 scenarios', 474, 190, 270, 43, { size: 30, bold: true, color: C.navy });
  text(s, 'steady · wave · brake', 474, 241, 300, 38, { size: 17, color: C.muted });
  line(s, 813, 156, 813, 590, C.rule, 1.4);
  text(s, 'HOLDOUT', 864, 155, 270, 21, { size: 13, bold: true, color: C.amber });
  text(s, '2 stresses', 864, 190, 270, 43, { size: 30, bold: true, color: C.navy });
  text(s, 'synthetic gap drop + brake\nhigher-speed emergency brake', 864, 241, 320, 66, { size: 17, color: C.muted });
  line(s, 58, 352, 1220, 352, C.rule, 1.2);
  const ctl = [['CTG-PID', C.blue], ['MPC', C.amber], ['Residual Q', C.teal], ['Q + guard', C.navy]];
  ctl.forEach((a, i) => {
    const x = 58 + i * 291;
    addShape(s, 'rect', x, 403, 8, 42, a[1]);
    text(s, a[0], x + 20, 405, 250, 34, { size: 22, bold: true, color: C.ink });
  });
  text(s, '5 scenario families × 4 controllers × 50 seeds = 1,000 episodes', 58, 514, 1080, 43, { size: 25, bold: true, color: C.navy });
  text(s, '600 training-family episodes + 400 held-out stress episodes. Each seed is matched across controllers.', 58, 566, 1085, 38, { size: 16, color: C.muted });
  notes(s, 'Training: 6,000 episodes on steady, wave and moderate braking. Evaluation: 50 seeds for each of five scenario families and four controllers, totalling 1,000. That is 600 training-family episodes and 400 held-out cut-in/emergency episodes. Each seed randomizes initial conditions and, for holdouts, event settings; all four controllers see the same seed. We report episode means, sample SDs and approximate 95% intervals. Cut-in onset is 6–10 s, gap loss is 16–26 m, and lead braking is 3.5–5.0 m/s² for 2–3 s. This is still a longitudinal distance-step approximation, not lane geometry.');
}

// 8 — Tracking chart
{
  const s = baseSlide('07 · Results · tracking', 'MPC tracks the chosen gap best in both test groups.', 8);
  addChart(s, 'bar', {
    position: { left: 58, top: 145, width: 1164, height: 440 },
    title: 'Episode gap RMSE (m) · mean across scenarios and seeds',
    titlePlacement: 'aboveChart',
    categories: ['CTG-PID', 'MPC', 'Residual Q', 'Q + guard'],
    series: [
      { name: 'Common profiles (150 episodes)', values: [2.46, 1.75, 3.24, 3.24], fill: C.blue },
      { name: 'Held-out stresses (100 episodes)', values: [3.58, 2.36, 4.77, 3.91], fill: C.amber },
    ],
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 90 },
    hasLegend: true,
    legend: { position: 'bottom', overlay: false, textStyle: { fill: C.muted, fontSize: 13 } },
    yAxis: { title: { text: 'RMSE (m)', textStyle: { fill: C.muted, fontSize: 13 } }, min: 0, max: 6, majorUnit: 1, numberFormatCode: '0.0', textStyle: { fill: C.muted, fontSize: 13 }, majorGridlines: { style: 'solid', fill: C.rule, width: 1 } },
    xAxis: { textStyle: { fill: C.ink, fontSize: 14 }, majorGridlines: null },
    dataLabels: { showValue: true, position: 'outEnd', numberFormatCode: '0.00', textStyle: { fill: C.navy, fontSize: 12, bold: true } },
  });
  text(s, 'The learned policy does not beat either classical baseline on gap tracking.', 58, 606, 1060, 30, { size: 18, bold: true, color: C.tealDark });
  notes(s, 'Mean episode gap RMSE, lower is closer to the target. Common profiles combine 150 episodes (three scenarios × 50); held-out stresses combine 100 episodes (two × 50). MPC is lowest at 1.75 m and 2.36 m. CTG-PID is 2.46 m and 3.58 m. Residual Q is 3.24 m and 4.77 m; Q+guard is 3.24 m and 3.91 m. Approximate 95% intervals for the group means: common-profile CTG [2.20,2.72], MPC [1.55,1.95], Q [2.86,3.61]; holdout CTG [3.08,4.07], MPC [2.06,2.65], Q [4.29,5.25], Q+guard [3.58,4.23]. This is model simulation evidence.');
}

// 9 — Comfort chart
{
  const s = baseSlide('08 · Results · comfort', 'The cut-in safety gain comes with sharper acceleration changes.', 9, { titleSize: 31 });
  addChart(s, 'bar', {
    position: { left: 58, top: 145, width: 860, height: 435 },
    title: 'Mean absolute jerk (m/s³)',
    titlePlacement: 'aboveChart',
    categories: ['CTG-PID', 'MPC', 'Residual Q', 'Q + guard'],
    series: [
      { name: 'Common profiles', values: [0.216, 0.268, 0.505, 0.505], fill: C.blue },
      { name: 'Held-out stresses', values: [0.282, 0.579, 0.738, 0.850], fill: C.amber },
    ],
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 80 },
    hasLegend: true,
    legend: { position: 'bottom', overlay: false, textStyle: { fill: C.muted, fontSize: 13 } },
    yAxis: { title: { text: 'm/s³', textStyle: { fill: C.muted, fontSize: 13 } }, min: 0, max: 1.0, majorUnit: 0.2, numberFormatCode: '0.0', textStyle: { fill: C.muted, fontSize: 13 }, majorGridlines: { style: 'solid', fill: C.rule, width: 1 } },
    xAxis: { textStyle: { fill: C.ink, fontSize: 13 }, majorGridlines: null },
    dataLabels: { showValue: true, position: 'outEnd', numberFormatCode: '0.000', textStyle: { fill: C.navy, fontSize: 11, bold: true } },
  });
  line(s, 955, 164, 955, 582, C.rule, 1.3);
  text(s, 'Cut-in comparison', 989, 175, 220, 28, { size: 20, bold: true, color: C.navy });
  text(s, 'Q mean |jerk|', 989, 226, 208, 26, { size: 15, bold: true, color: C.muted });
  text(s, '0.957', 989, 255, 220, 42, { size: 31, bold: true, color: C.tealDark });
  text(s, 'Q + guard', 989, 335, 205, 26, { size: 15, bold: true, color: C.muted });
  text(s, '1.222', 989, 365, 220, 42, { size: 31, bold: true, color: C.amber });
  text(s, 'm/s³ · 25.8 guard edits per run', 989, 417, 220, 49, { size: 16, color: C.ink });
  text(s, 'Lower jerk is usually smoother; it is only a comfort proxy.', 989, 500, 220, 63, { size: 16, color: C.muted });
  notes(s, 'Jerk is the rate of change of acceleration and a rough ride-comfort proxy. Across all scenarios, CTG-PID has the lowest mean absolute jerk. In the cut-in family, Q had 0.957 m/s³ and Q+guard 1.222 m/s³. The guard changed the action 25.8 times per 400-step episode on average (6.46% of steps). Paired Q+guard minus Q jerk was +0.265 m/s³, approximate 95% interval [+0.239,+0.290]. The guard effect is visible but comes with a real smoothness cost.');
}

// 10 — Cut-in result
{
  const s = baseSlide('09 · Results · cut-in', 'The guard helps Q on near-conflict measures; MPC remains stronger.', 10, { titleSize: 30 });
  addChart(s, 'bar', {
    position: { left: 58, top: 151, width: 735, height: 420 },
    title: 'Mean episode minimum gap · 50 matched cut-in runs per controller (m)',
    titlePlacement: 'aboveChart',
    categories: ['CTG-PID', 'MPC', 'Residual Q', 'Q + guard'],
    series: [{ name: 'Minimum gap', values: [8.58, 13.11, 7.00, 11.35], fill: C.teal }],
    barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 80 },
    hasLegend: false,
    yAxis: { title: { text: 'm', textStyle: { fill: C.muted, fontSize: 13 } }, min: 0, max: 15, majorUnit: 3, numberFormatCode: '0', textStyle: { fill: C.muted, fontSize: 13 }, majorGridlines: { style: 'solid', fill: C.rule, width: 1 } },
    xAxis: { textStyle: { fill: C.ink, fontSize: 13 }, majorGridlines: null },
    dataLabels: { showValue: true, position: 'outEnd', numberFormatCode: '0.00', textStyle: { fill: C.navy, fontSize: 12, bold: true } },
  });
  line(s, 835, 164, 835, 590, C.rule, 1.3);
  labelValue(s, 'Q closing samples TTC < 2 s', '2.04%', 881, 168, 300, C.red);
  text(s, 'Q + guard: 0% in these 50 runs', 881, 252, 312, 27, { size: 18, bold: true, color: C.tealDark });
  labelValue(s, 'Guarded Q − Q minimum gap', '+4.35 m', 881, 310, 308, C.amber);
  text(s, 'Q jerk 0.957 → guarded Q 1.222 m/s³\n25.8 action edits per episode', 881, 405, 315, 61, { size: 16, color: C.ink });
  text(s, 'No collisions in 50 cut-in episodes; this is not a safety guarantee.', 881, 508, 315, 52, { size: 16, bold: true, color: C.navy });
  text(s, 'A cut-in is an instantaneous gap drop in this model; no lane-change dynamics.', 58, 606, 1110, 30, { size: 16.5, color: C.muted });
  notes(s, 'Across 50 randomized and seed-matched cut-in episodes, unfiltered Q had a 7.00 m mean episode minimum gap (sample SD 3.14) and TTC below 2 seconds during 2.04% of closing samples. Q+guard raised mean minimum gap to 11.35 m and had zero observed TTC<2 exposure in these runs. Paired Q+guard minus Q minimum gap was +4.355 m, approximate 95% interval [+4.026,+4.683]; paired short-TTC exposure change was −2.037 percentage points, interval [−3.138,−0.936]. MPC still had the best cut-in gap RMSE (3.76 m) and largest mean minimum gap (13.11 m). The guard changed the Q action about 25.8 times per episode and increased jerk. No collision occurred in these 50 cut-in simulations; that is not a risk estimate or proof.');
}

// 11 — One matched cut-in trajectory
{
  const s = baseSlide('10 · Results · one example', 'Same cut-in, four controllers: follow the gap after the event.', 11, { titleSize: 32 });
  const plottedControllers = [
    ['CTG-PID', C.blue], ['MPC', C.amber], ['Q-Learning', C.teal], ['Q+RSS', C.navy],
  ];
  const cutinRows = representativeTraces.filter(row => row.scenario === 'cut_in');
  const firstControllerRows = cutinRows.filter(row => row.controller === plottedControllers[0][0]);
  const sampleIndexes = firstControllerRows.map((_, index) => index).filter(index => index % 20 === 0);
  if (firstControllerRows.length - 1 > sampleIndexes.at(-1)) sampleIndexes.push(firstControllerRows.length - 1);
  const categories = sampleIndexes.map(index => Number(firstControllerRows[index].t).toFixed(0));
  const lineSeries = plottedControllers.map(([name, color]) => {
    const values = cutinRows.filter(row => row.controller === name);
    return { name, values: sampleIndexes.map(index => Number(Number(values[index].gap).toFixed(2))), fill: color };
  });
  addChart(s, 'line', {
    position: { left: 58, top: 145, width: 1164, height: 438 },
    title: `Bumper gap over time · representative seed ${experimentManifest.representative_trace_seed}`,
    titlePlacement: 'aboveChart',
    categories,
    series: lineSeries,
    hasLegend: true,
    legend: { position: 'bottom', overlay: false, textStyle: { fill: C.muted, fontSize: 13 } },
    yAxis: { title: { text: 'Gap (m)', textStyle: { fill: C.muted, fontSize: 13 } }, min: 0, max: 60, majorUnit: 10, numberFormatCode: '0', textStyle: { fill: C.muted, fontSize: 13 }, majorGridlines: { style: 'solid', fill: C.rule, width: 1 } },
    xAxis: { title: { text: 'Time (s)', textStyle: { fill: C.muted, fontSize: 13 } }, textStyle: { fill: C.ink, fontSize: 12 }, majorGridlines: null },
  });
  text(s, 'One trajectory helps explain the event; the 50-episode averages above carry the comparison.', 58, 606, 1120, 30, { size: 17, bold: true, color: C.tealDark });
  notes(s, 'This is one matched cut-in seed chosen for a readable example, not a cherry-picked summary. All controllers receive the same onset, gap reduction, lead braking, initial speeds and starting gap. The abrupt discontinuity in gap is intentional in the model. The aggregate claims come from 50 randomized episodes per controller in the preceding result slides. The MP4 simulation clip can be played alongside this chart.');
}

// 12 — Current commercial ACC reference
{
  const s = baseSlide('11 · Production reference', 'Current commercial ACC already reacts to cut-ins; our evidence is narrower.', 12, { titleSize: 30 });
  const cards = [
    { x: 58, w: 355, title: 'CURRENT PRODUCT', color: C.blue,
      big: '2025 Honda Accord Hybrid', body: 'Owner manual describes a selectable following interval and a warning when a lead slows abruptly or another car cuts in.' },
    { x: 461, w: 355, title: 'REAL-ROAD REFERENCE', color: C.teal,
      big: 'OpenACC · 5,505 samples', body: 'One 2019 minimum-distance run: median observed time headway 1.31 s; our 5 m + 1.3v target implies 1.46 s at the same speed.' },
    { x: 864, w: 358, title: 'FAIR COMPARISON', color: C.amber,
      big: 'No product winner claimed', body: 'The field trace is not a cut-in challenge; the owner manual does not expose control gains. We compare our algorithms in simulation.' },
  ];
  cards.forEach((c, i) => {
    if (i) line(s, c.x - 24, 155, c.x - 24, 570, C.rule, 1.2);
    text(s, c.title, c.x, 162, c.w, 22, { size: 13, bold: true, color: c.color });
    text(s, c.big, c.x, 204, c.w, 59, { size: 23, bold: true, color: C.navy });
    text(s, c.body, c.x, 284, c.w, 137, { size: 18, color: C.ink });
  });
  addShape(s, 'roundRect', 58, 467, 1164, 99, C.paleTeal, C.rule, 1, 'comparison-boundary', { borderRadius: 10 });
  text(s, 'What we can say', 81, 486, 198, 24, { size: 16, bold: true, color: C.tealDark });
  text(s, 'Guarded Q improved two cut-in indicators versus unguarded Q. MPC still had better simulated gap tracking and a larger minimum gap.', 266, 483, 921, 58, { size: 17, bold: true, color: C.navy });
  text(s, 'OpenACC is a 2019 field dataset; Honda’s official 2025 owner manual is a feature reference, not a public controller benchmark.', 58, 606, 1150, 28, { size: 15.5, color: C.muted });
  notes(s, 'This is the requested production comparison, bounded carefully. Honda’s official 2025 Accord Hybrid manual describes a settable following interval and a warning if the lead vehicle slows abruptly or another vehicle cuts in; it does not publish a controller we can replay. For data context, the European Commission JRC OpenACC database includes on-road runs of commercial ACC systems. We analyzed one Vicolungo 2019 trace: a Human-driven Mitsubishi SpaceStar leads a Ford S-Max with ACC at minimum distance setting; 5,505 interpolated samples span 550.4 s; observed median time headway is 1.314 s. Because the original GNSS data were 3–5 Hz and spline-interpolated to 10 Hz, we avoid claiming high-frequency jerk from it. At the median follower speed of 31.36 m/s, our project target 5+1.3v equals 45.77 m, or 1.459 s effective headway. This is a descriptive reference, not a same-condition cut-in test. The commercial control logic is not a directly available benchmark, so we make no claim that our RL beats a production car. Sources: Honda owner manual https://techinfo.honda.com/rjanisis/pubs/om/ah/a30b2525iom/enu/details/131245047-520366.html; JRC OpenACC dataset https://data.jrc.ec.europa.eu/dataset/9702c950-c80f-4d2f-982f-44d06ea0009f; Makridis et al. 2021, https://doi.org/10.1016/j.trc.2021.103047.');
}

// 13 — Iteration / own work
{
  const s = baseSlide('12 · Own work', 'The first Q policy failed; the learned correction improved it but did not win.', 13, { titleSize: 29 });
  text(s, 'ABSOLUTE ACTION PILOT', 58, 160, 320, 21, { size: 13, bold: true, color: C.red });
  text(s, '15.20 m', 58, 199, 270, 54, { size: 40, bold: true, color: C.red });
  text(s, 'in-distribution gap RMSE', 58, 259, 295, 27, { size: 17, color: C.muted });
  text(s, '1 / 24', 58, 319, 270, 48, { size: 32, bold: true, color: C.navy });
  text(s, 'episodes had a collision', 58, 369, 295, 28, { size: 17, color: C.muted });
  line(s, 420, 160, 420, 548, C.rule, 1.4);
  text(s, 'RESIDUAL Q REDESIGN', 476, 160, 350, 21, { size: 13, bold: true, color: C.tealDark });
  text(s, 'CTG-PID action', 476, 209, 260, 35, { size: 25, bold: true, color: C.navy });
  text(s, '+ one of seven learned corrections', 476, 258, 530, 34, { size: 21, color: C.ink });
  text(s, 'zero residual on ties / unvisited bins', 476, 309, 545, 31, { size: 19, color: C.tealDark });
  line(s, 476, 373, 1188, 373, C.rule, 1);
  text(s, 'MEAN GAP RMSE · 150 COMMON-PROFILE EPISODES EACH', 476, 406, 690, 20, { size: 13, bold: true, color: C.tealDark });
  text(s, 'CTG-PID', 476, 445, 180, 21, { size: 14, bold: true, color: C.blue });
  text(s, '2.46 m', 476, 475, 180, 42, { size: 31, bold: true, color: C.navy });
  text(s, 'MPC', 712, 445, 180, 21, { size: 14, bold: true, color: C.amber });
  text(s, '1.75 m', 712, 475, 180, 42, { size: 31, bold: true, color: C.navy });
  text(s, 'Residual Q', 948, 445, 190, 21, { size: 14, bold: true, color: C.tealDark });
  text(s, '3.24 m', 948, 475, 190, 42, { size: 31, bold: true, color: C.navy });
  text(s, 'The pilot is archived; final results use the revised, separately trained table.', 58, 593, 1090, 30, { size: 17, bold: true, color: C.navy });
  notes(s, 'This slide shows our own design iteration. The absolute-action Q pilot had 15.20 m in-distribution RMSE and one collision in 24 episodes. We retained it, then switched to residual Q so the nominal CTG controller remains active. In the expanded common-profile comparison (150 episodes per controller), CTG-PID mean RMSE was 2.46 m, MPC 1.75 m, and residual Q 3.24 m. The guard does not reverse that overall ranking. This is a negative performance result and a positive engineering lesson about keeping a transparent baseline in the loop.');
}

// 14 — Conclusion
{
  const s = baseSlide('13 · Conclusion', 'So, is the RL controller better?', 14, { dark: true, titleSize: 42, titleH: 86 });
  const takeaway = [
    ['OVERALL', 'No. MPC had the lowest gap error.'],
    ['CUT-IN', 'Guarded Q improved Q’s minimum gap and short-TTC exposure.'],
    ['COST', 'The guard increased jerk and changed the action often.'],
  ];
  takeaway.forEach((a, i) => {
    const x = 67 + i * 387;
    if (i) line(s, x - 26, 230, x - 26, 421, '#355063', 1.2);
    text(s, a[0], x, 230, 320, 20, { size: 13, bold: true, color: i === 2 ? C.amber : C.teal });
    text(s, a[1], x, 273, 315, 111, { size: 22, bold: true, color: C.white });
  });
  addShape(s, 'rect', 67, 473, 8, 89, C.amber);
  text(s, 'Better than unguarded Q on this cut-in stress—not better than the classical or commercial references overall.', 96, 483, 1060, 62, { size: 21, bold: true, color: C.white });
  text(s, 'Next: replay an annotated real cut-in with a vehicle-calibrated model and sensor delay.', 67, 607, 1080, 29, { size: 17, color: '#C8D4DC' });
  notes(s, 'Answer the examiner plainly. The safety guard improved Q relative to Q in this randomized cut-in family: mean minimum gap rose from 7.00 to 11.35 m and time with TTC<2 s went from 2.04% to zero across the 50 runs. But MPC still had the lowest cut-in gap RMSE (3.76 m) and the largest mean minimum gap (13.11 m). Guarded Q also had the highest mean absolute jerk among these cut-in methods. We have not run our policy head-to-head with a commercial car; the OpenACC sample is context and Honda’s manual is a feature comparison. This project demonstrates a focused, reproducible experiment, not vehicle readiness.');
}

// 15 — References, control and RL
{
  const s = baseSlide('References · 1 of 2', 'ACC control and reinforcement learning', 15, { titleSize: 32 });
  const refs = [
    'Bageshwar, V. L., Garrard, W. L., & Rajamani, R. (2004). Model predictive control of transitional maneuvers for adaptive cruise control vehicles. IEEE Transactions on Vehicular Technology, 53(5), 1573–1585. DOI: 10.1109/TVT.2004.833625.',
    'Li, S. E., Li, K., Rajamani, R., & Wang, J. (2011). Model predictive multi-objective vehicular adaptive cruise control. IEEE Transactions on Control Systems Technology, 19(3), 556–566. DOI: 10.1109/TCST.2010.2049203.',
    'He, Y. et al. (2019). Adaptive cruise control strategies implemented on experimental vehicles: A review. IFAC-PapersOnLine, 52(5), 21–27. DOI: 10.1016/j.ifacol.2019.09.004.',
    'Makridis, M., Mattas, K., Anesiadou, A., & Ciuffo, B. (2021). OpenACC: An open database of car-following experiments to study commercial ACC systems. Transportation Research Part C, 125, 103047. DOI: 10.1016/j.trc.2021.103047.',
    'Watkins, C. J. C. H., & Dayan, P. (1992). Q-learning. Machine Learning, 8, 279–292. DOI: 10.1007/BF00992698.',
    'Desjardins, C., & Chaib-draa, B. (2011). Cooperative adaptive cruise control: A reinforcement learning approach. IEEE Transactions on Intelligent Transportation Systems, 12(4), 1248–1260. DOI: 10.1109/TITS.2011.2157145.',
    'Zhu, M., Wang, X., & Wang, Y. (2018). Human-like autonomous car-following model with deep reinforcement learning. Transportation Research Part C, 97, 348–368. DOI: 10.1016/j.trc.2018.10.024.',
    'Zhu, M. et al. (2020). Safe, efficient, and comfortable velocity control based on reinforcement learning for autonomous driving. Transportation Research Part C, 117, 102662. DOI: 10.1016/j.trc.2020.102662.',
    'Lin, Y., McPhee, J., & Azad, N. L. (2021). Comparison of deep reinforcement learning and model predictive control for adaptive cruise control. IEEE Transactions on Intelligent Vehicles, 6, 221–231. DOI: 10.1109/TIV.2020.3012947.',
  ];
  refs.forEach((r, i) => {
    const y = 145 + i * 52;
    addShape(s, 'ellipse', 61, y + 5, 7, 7, i < 4 ? C.blue : C.teal);
    text(s, r, 80, y, 1110, 47, { size: 13.5, color: C.ink });
  });
  notes(s, 'These references support ACC/MPC, field data and RL claims. The course guide contains a broader critical review and paper-analysis matrix. Consult full papers before repeating paper-level numerical results.');
}

// 16 — References, safety
{
  const s = baseSlide('References · 2 of 2', 'Safety methods, production manual, dataset and standards', 16, { titleSize: 30 });
  const refs = [
    'Swaroop & Hedrick (1996). String stability of interconnected systems. IEEE Transactions on Automatic Control, 41(3), 349–357. DOI: 10.1109/9.486636.',
    'Ames et al. (2014). Control barrier function based quadratic programs with application to adaptive cruise control. IEEE CDC. DOI: 10.1109/CDC.2014.7040372.',
    'Shalev-Shwartz, Shammah & Shashua (2017). On a formal model of safe and scalable self-driving cars. arXiv:1708.06374.',
    'Alshiekh et al. (2018). Safe reinforcement learning via shielding. AAAI, 32(1), 2669–2678. DOI: 10.1609/AAAI.V32I1.11797.',
    'Hailemichael et al. (2022). Safety filtering for reinforcement learning-based adaptive cruise control. IFAC-PapersOnLine, 55(24). DOI: 10.1016/j.ifacol.2022.10.276.',
    'Vogel (2003). A comparison of headway and time to collision as safety indicators. Accident Analysis & Prevention, 35(3), 427–433. DOI: 10.1016/S0001-4575(02)00022-2.',
    'Honda (2025). Accord Hybrid owner’s manual: Adaptive Cruise Control with Low Speed Follow. techinfo.honda.com/rjanisis/pubs/om/ah/a30b2525iom/enu/details/131245047-520366.html.',
    'European Commission Joint Research Centre. Open ACC Database, Vicolungo sample, DOI: 10.2905/JRC.KMH3D00. data.jrc.ec.europa.eu/dataset/9702c950-c80f-4d2f-982f-44d06ea0009f.',
    'ISO 15622:2018, ACC performance requirements and test procedures; ISO/DIS 15622 is the revision under development. iso.org/standard/71515.html; iso.org/standard/89465.html.',
    'ISO 21448:2022. Road vehicles — Safety of the intended functionality (SOTIF). iso.org/standard/77490.html.',
  ];
  refs.forEach((r, i) => {
    const y = 143 + i * 46;
    addShape(s, 'ellipse', 61, y + 5, 7, 7, i < 6 ? C.amber : C.teal);
    text(s, r, 80, y, 1110, 42, { size: 12.2, color: C.ink });
  });
  text(s, 'Our guard is RSS-inspired; it is not a formal RSS, CBF, SOTIF assessment or certification.', 58, 625, 1120, 25, { size: 15.5, bold: true, color: C.tealDark });
  notes(s, 'Safety terminology references: Ames et al. 2014 is an ACC-specific CBF-QP study; RSS is a safe-distance model; shielding filters actions against modeled specifications; ISO 15622 covers ACC performance requirements and test procedures; ISO 21448 provides a SOTIF framework. Our simplified guard does not implement or inherit a formal guarantee. The Honda link is a production-feature reference; the OpenACC citation describes the data used for the headway context. ISO/DIS 15622 was registered as a draft revision as of this project date.');
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(outDir, { recursive: true });
  await fs.mkdir(buildDir, { recursive: true });
  await fs.mkdir(slideDir, { recursive: true });

  for (const [i, slide] of presentation.slides.items.entries()) {
    const png = await presentation.export({ slide, format: 'png', scale: 1 });
    await writeBlob(path.join(slideDir, `slide-${String(i + 1).padStart(2, '0')}.png`), png);
  }

  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(candidatePath);

  const skillDir = '/Users/rajpratapsinghgurjar/.codex/plugins/cache/openai-primary-runtime/presentations/26.1013.11914/skills/presentations';
  const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, 'container_tools/artifact_tool_utils.mjs')).href);
  const result = await finalizePresentation({
    workspaceDir: root,
    candidatePath,
    finalPath,
    pythonExecutable: '/Users/rajpratapsinghgurjar/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3',
    integrityValidatorPath: path.join(skillDir, 'container_tools/inspect_presentation_package_integrity.py'),
    layoutValidatorPath: path.join(skillDir, 'container_tools/inspect_presentation_layout_geometry.py'),
    layoutArgs: ['--expected-slide-size-emu', '12192000,6858000', '--validate-heading-fit'],
    explicitTotalSlideCount: 16,
    requiredNativeChartOwnerSlides: [8, 9, 10, 11],
    requiredNativeTableOwnerSlides: [],
    materializeLiteralChartWorkbooks: true,
    fontPolicy: { basis: 'design', families: ['Arial'] },
    verifyArtifactToolImport: true,
    receiptPath: path.join(buildDir, 'ACC_RL_CutIn_Focused_Presentation.validation.json'),
  });
  console.log(JSON.stringify(result, null, 2));
  console.log(`Rendered previews: ${slideDir}`);
  console.log(`Final presentation: ${finalPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
