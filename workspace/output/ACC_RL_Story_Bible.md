# ACC cut-in film: story and character bible

## Film premise

An understandable ACC learner earns trust only when its gap response and comfort costs are measured against clear control references.

## Creative thesis and counterpoint

The film makes the project legible through one question: can a small learned correction help a familiar adaptive-cruise controller when the following gap changes suddenly? The counterpoint stays visible throughout: a hand-built braking guard adds another rule, can make the response rougher, and does not beat the simplified MPC reference on every measure.

## World sheet

- **Physical:** One university automotive-controls lab after dusk; a shared matte display, charcoal workbench, two stools, one desk lamp, and small unbranded vehicle models.
- **Social:** Mira owns the project hypothesis; Dev checks the evidence. They are classmates and collaborators, not hero and skeptic. They both want a result they can defend in front of their course instructor.
- **Economic:** A laptop-sized project budget. The learning policy is a finite Q table, not a neural-network training stack.
- **Ideological:** Measured results outrank a claim that AI is automatically better. Comfort is reported beside following gap.
- **Historical:** Their first hypothesis was that the learned correction might improve the cut-in response. The data gives them a more specific conclusion: the guard helps Q-learning on two gap-risk measures, raises jerk, and leaves MPC ahead on minimum gap and jerk.
- **Sensory:** Teal light from the display, one warm desk lamp, graphite marks on paper, quiet ventilation, a soft interface click.

## Character sheets

### Mira — project researcher

- **Role:** Main researcher, focused on making a small learned correction useful in an automotive-control setting.
- **Objective:** Get Dev to examine the result carefully enough to make a defensible claim.
- **Need:** Let the measured trade-off revise the original hypothesis.
- **Contradiction:** She likes the elegance of the Q-learning idea and is willing to expose its weak points.
- **Silhouette:** Compact stance, straight black bob with a left part, teal crewneck, orange lanyard, notebook and pencil.
- **Voice lock:** Clear Indian-English classroom delivery; medium pace; warm, direct, precise with units; finishes numerical claims without a sales lift.
- **Movement lock:** Traces a single axis with the pencil; when a result surprises her, the pencil stops before she looks back to Dev.
- **Height lock:** 165 cm.

**Acting master profile:** Character acting as Mira. Compact, balanced build; her shoulders stay open and her weight settles evenly when she studies a chart. Her drive makes a control idea understandable enough that another student can challenge it. Vocal profile: clear medium pitch, Indian-English accent, measured classroom pace; her sentences tighten slightly when defending a result, then slow when revising it. Key physical habits and tics: she traces a single axis with her pencil while explaining; when a comfort metric conflicts with her hypothesis, the pencil stops and her lower lip presses for one beat; she conceals attachment by turning the notebook toward Dev and asking him to check the number. Her facial mask is composed concentration. However, when the jerk value rises, her chin lowers, breath pauses, eyes return to the row, and the mask opens into a small acknowledging nod. Eye life: her standing task is Dev's face, then the same chart detail his pencil follows; she blinks every few seconds, scans left to right across one row, and lets her gaze move before her head. Walking style: a "survey walk," short heel-to-toe steps at an even pace, notebook close to her ribs, eyes arriving at the display before her torso. However, when a result changes her conclusion, she stops mid-step, checks the figure, then reopens her shoulders toward Dev.

### Dev — validation partner

- **Role:** Teammate responsible for checking whether the comparison is fair and whether the comfort cost is visible.
- **Objective:** Make Mira place the jerk result and MPC reference beside the gap result.
- **Need:** Keep skepticism useful by letting a measured benefit count when it appears.
- **Contradiction:** He expects the classical reference to hold up, yet he is willing to recognize a real improvement in the guarded Q result.
- **Silhouette:** Tall, slim stance, short textured black curls, round dark glasses, indigo work shirt with an amber cuff, red mechanical pencil.
- **Voice lock:** Calm Indian-English classroom delivery; lower register; compact phrasing; slight pause before challenging a number; neutral emphasis on comparisons.
- **Movement lock:** Keeps the red pencil near the current chart; taps once at the metric that changes his reading, then lowers it while listening.
- **Height lock:** 178 cm.

**Acting master profile:** Character acting as Dev. Tall, lean build with a low, settled center of gravity; he keeps his shoulders angled toward the display and uses small deliberate movements. His psychological engine is to keep the team's claim fair enough to survive a comparison. Vocal profile: low, calm register, Indian-English accent, compact phrasing; a short pause comes before a challenge, and his cadence softens when the data supports Mira. Key physical habits and tics: he holds a red pencil near the active row while listening; when the seed match is unclear, he taps the same row twice; he conceals agreement by checking the next metric before nodding. His facial mask is neutral concentration. However, when the gap result improves more than he expected, one brow lifts and his pencil stops; the mask cracks into a brief half-smile before he checks the jerk row. Eye life: his standing task is to verify the number Mira names, then return to her face; he blinks slowly, scans along a row rather than around the room, and lets his eyes lead each head turn. Walking style: a "level walk," long quiet heel-to-toe steps with even foot placement, arms close, and head level. However, when the comfort cost appears, he stops at the chart, leans a fraction closer, and points once before looking back to Mira.

## Character web and scene engine

- **Shared direction:** Finish one honest course-project explanation together.
- **Essential contrast:** Mira presses the hypothesis into a test; Dev pressures the test into a fair comparison. Each moves toward a more careful conclusion.
- **Primary obstacle:** The result is mixed, so a simple “AI wins” ending is not supported.
- **Midpoint turn:** The guard improves mean minimum gap by 4.35 m and lowers the low-TTC share in the cut-in results, then its higher mean absolute jerk appears. The group must report both.

## Seven-beat story spine

1. A sudden gap change gives Mira a clear ACC question; Dev asks that the comfort cost be included.
2. They show why a cut-in challenges following-gap control and explain that this simulator represents it as an instantaneous gap step.
3. Mira reveals the small Q residual on the CTG-PID base; Dev checks the simplified braking guard that filters a proposed action.
4. They disclose 6,000 training episodes, held-out cut-in/emergency families, and a matched-seed evaluation.
5. The side-by-side result shows Q-learning without the guard and Q-learning with it across the same 50 cut-in seeds.
6. The jerk metric complicates the result; the MPC reference remains better on cut-in mean minimum gap and mean absolute jerk.
7. The pair agree on the honest conclusion and propose replaying measured cut-ins with lane, sensing, and delay models.

## Locked visual DNA

- **Palette:** 60% midnight navy `#09111D`; 30% slate/teal `#10243A` and `#4DDCCD`; 10% amber `#FFBE69`, violet `#B697FF`, and red `#FF7082` for alert states.
- **Lighting:** One 4000K desk practical from camera-left; soft teal screen spill; faces remain naturally shaded and readable.
- **Materials:** Matte screen, brushed aluminum, charcoal desk, paper, pencil, soft textile clothing.
- **Juxtaposition:** Human-scale classroom work beside precise technical plots.
- **Forbidden list:** No brand marks, no fake dashboard text, no glowing sci-fi cockpit, no floating HUDs over a real road, no lane-change animation presented as the simulator, no collision footage, no safety-certification language.
- **Continuity:** Reuse the three supplied PNG reference images and the exact identity blocks in every shot. Exact metrics, labels, axes and conclusions are composited from the project CSVs in the final edit.

## Evidence locks

All values below are means from 50 matched synthetic cut-in episodes per controller in `outputs/formal_50seed/scenario_summary.csv`.

| Controller | Mean episode minimum gap | Mean share of closing samples with TTC < 2 s | Mean absolute jerk |
|---|---:|---:|---:|
| CTG-PID | 8.58 m | 0.40% | 0.26 m/s³ |
| Q-learning | 7.00 m | 2.04% | 0.96 m/s³ |
| Q + simplified guard | 11.35 m | 0.00% | 1.22 m/s³ |
| Simplified MPC | 13.11 m | 0.00% | 0.63 m/s³ |

The guard is RSS-inspired, simplified, and is not formal RSS. The simulation is a one-dimensional point-mass model with an instantaneous gap drop. Zero observed collisions in this scenario set is not a safety guarantee. The comparison does not test a production ACC system.

