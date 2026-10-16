# ACC cut-in explainer — video notes

## Storyboard

| Film time | Picture | Spoken line (optional) |
|---|---|---|
| 0:00–0:04 | Dark technical opening; two side-on vehicles and a shrinking measured gap. | “When the following gap shrinks suddenly, can a small safety rule help a learning-based cruise controller?” |
| 0:04–0:11 | Three-step method: tabular Q correction, braking-distance action filter, measured comparison. | “We add a small Q-learning correction to a familiar constant-time-gap controller, then test a braking-distance filter against classical PID and predictive control.” |
| 0:11–0:31 | Three synchronized cards play the recorded Q, Q+guard and MPC traces from matched seed 17. The plotted gap and vehicle spacing come from the trace. | “Each controller sees the same scripted event. This cut-in is represented as an instantaneous longitudinal gap drop, so the view is one-dimensional.” |
| 0:31–0:41 | Aggregate minimum-gap bars for 50 randomized matched cut-in episodes; TTC and jerk trade-off figures. | “Across 50 matched runs, the guard raised Q’s mean episode minimum gap by about 4.35 metres and reduced the share of closing samples with TTC below two seconds from 2.04 percent to zero. Mean absolute jerk also rose.” |
| 0:41–0:48 | Finding and scope card. | “MPC still had the largest mean minimum gap in this scenario set. These are simulation results, not a production-car comparison. Next, replay measured cut-in trajectories and add lane and sensor models.” |

The local MP4 is silent so the presenter can speak naturally over it. The optional narration above is about 100 words and can also be used as a live intro.

## Higgsfield opener prompt

This is an optional mood-setting shot. It is not the source of the measured comparison; the delivered film is rendered from the project’s CSV traces and summary file.

**Model:** Kling v3.0 · standard mode  
**Aspect ratio:** 16:9 · **Duration:** 8 seconds · **Style:** Cinematic

**M — Model:** Kling v3.0.  
**C — Camera:** Dolly In, one smooth move toward the measured distance between the vehicles.  
**S — Subject:** Two unbranded modern passenger cars following one another on a clean closed test track at blue hour; a restrained teal sensor arc spans the visible gap.  
**L — Look:** Cinematic automotive technology film, midnight-navy environment, cool teal and warm amber edge lights, sharp focus throughout, deep depth of field.  
**A — Action:** The cars hold their lane and scale as a single teal measurement pulse travels across the gap and the distance marker tightens slightly, then steadies. The camera eases forward and ends on the clear space between the cars. Keep the vehicle scale and spacing consistent; smooth, fluid motion, one action per shot; consistent lighting, no flicker.

The prompt follows the imported skill’s MCSLA structure and uses the verified `Dolly In` control. The skill’s 2026-09-26 model snapshot lists Kling v3.0 at 16:9 and 3–15 seconds, so the 8-second setting is within its documented range. Generated video should remain an opener only; it cannot replace the data-driven response sequence or serve as a safety result.

## Evidence and limits

- Representative episode: `outputs/formal_50seed/representative_traces.csv`, cut-in, seed 17.
- Aggregate comparison: `outputs/formal_50seed/scenario_summary.csv`, cut-in family, 50 seed-matched episodes per controller.
- Experiment definition: `outputs/formal_50seed/experiment_manifest.json`.
- The simple cut-in is an instantaneous longitudinal gap change with following lead braking. It has no lateral lane-change geometry, perception, or sensor-delay model.
- `CTG-PID` is the project’s classical ACC baseline. The project did not test a production car head-to-head; the Honda owner manual is feature context only.

## Skill source

Imported from [OSideMedia/higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill), MIT licensed, commit `70754977d1884794963ac0a748eaa85b6e9c82a`. Installed locally at `/Users/rajpratapsinghgurjar/.agents/skills/higgsfield-ai-prompt-skill`. The prompt uses its MCSLA, camera-control and shared prevention-constraint guidance.
