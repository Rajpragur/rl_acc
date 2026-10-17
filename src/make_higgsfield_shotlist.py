"""Build a copy-ready, character-led Higgsfield shotlist for the ACC project."""

from __future__ import annotations

from html import escape
from pathlib import Path


OUT = Path("workspace/output/ACC_RL_Higgsfield_Shotlist.html")

STYLE_PREFIX = """Style: A restrained 2.5D editorial animation built from matte illustrated shapes, fine paper texture and subtle dimensional light. The film stays grounded in one university automotive-controls lab after dusk. Lighting: one warm 4000K desk practical from camera-left and soft teal spill from the display; faces remain readable. Color Grade: 60% midnight navy #09111D, 30% slate #10243A and teal #4DDCCD, 10% amber #FFBE69 with violet #B697FF reserved for learned actions. Camera: deliberate, smooth physical moves; select shot size to serve the evidence. Acting: work-focused behavior, active eyes, measured pauses, restrained expressions. Physics: gravity, hand contact and paper weight read naturally. Composition: quiet negative space for post-edited titles and charts. Continuity: the attached character and lab references hold their identity, relative height, clothing and geometry across all cuts. Character consistency: Copy-paste exact character description across all prompts; separate Identity Block from Motion Block (see higgsfield-soul). Face stable. Body proportions consistent throughout. Matte monitor surfaces show simple flat shapes; exact text, labels, values and plotted data are composited in the final edit. Audio: quiet ventilation room tone and one soft pencil or interface tap tied to a visible action. Characters remain silent on screen; voiceover and score are added in post. NO BGM."""

MIRA = "Mira: a 165 cm graduate controls researcher with warm-brown complexion, a straight black shoulder-length bob with a left part, compact build, teal crewneck, orange lanyard, dark trousers and a small notebook. Identity Block stays fixed."
DEV = "Dev: a 178 cm validation partner with deep-brown complexion, short textured black curls, round dark glasses, tall lean build, indigo work shirt with an amber cuff and a red mechanical pencil. Identity Block stays fixed."
ENV = "The single lab from @Image3, full-preserve: charcoal workbench, one matte wide display, one desk lamp and two stools; the set contains only the referenced room geometry."

SCENES = [
    {
        "title": "A car-following question",
        "desc": "One university automotive-controls lab after dusk. Mira wants a small learned correction to prove useful; Dev wants the test to count comfort as well as spacing. They work at the same display, with the miniature traffic card centered between them.",
        "cuts": [
            ("5s", "Wide Shot / Two-Shot, 84° FOV, Camera Dolly In", "Both are already working. Mira traces the following-gap line with one pencil while Dev aligns two miniature vehicle markers. Their eyes meet when the gap on the monitor contracts; Mira slides one event card into the center of the desk. Warm desk light holds the faces against the teal display."),
            ("4s", "Medium Close-Up, 47° FOV, Camera Arc", "Mira stops the pencil at the narrowed gap and turns her eyes to Dev before her head follows. Dev lets her finish, then shifts his gaze to the comfort column and raises one brow. Keep the reaction small and specific; the measured pause carries the moment."),
            ("6s", "Insert Shot, 12° FOV, Camera Crane Down", "The notebook fills frame: one hand draws a single distance arrow between two simple car symbols while Dev's red pencil rests at the page edge. The two figures remain seated just beyond the insert. Hold the final mark for six seconds; paper and pencil stay physically grounded."),
        ],
    },
    {
        "title": "When the gap shrinks",
        "desc": "The lab display carries a schematic of the experiment. It shows one longitudinal following pair and an event marker; it is explicitly a gap-step proxy, not a lane-change scene.",
        "cuts": [
            ("5s", "Wide Shot / Two-Shot, 84° FOV, Camera Dolly Left", "The camera travels left across Mira and Dev toward a flat monitor diagram with two side-view car icons. A red event marker appears and the measured gap line shortens. The display uses clean geometry and blank bars; titles and exact values are added in post."),
            ("5s", "Medium Close-Up, 47° FOV, Camera Dolly In", "Mira's gaze moves from the event marker to the distance axis; she taps the start of the gap trace once. Dev follows the same axis with his eyes, holding still so her measurement reads. Their posture stays practical and collaborative."),
            ("5s", "Overhead Insert, 12° FOV, Camera Crane Down", "A single horizontal road-state bar shows EGO, LEAD and a vertical gap-step marker. The lead icon remains in its lane position; only longitudinal distance changes. Mira's finger holds at the measured interval while Dev's pencil marks the time axis. End on the clean one-dimensional diagram."),
        ],
    },
    {
        "title": "A small learner and a braking check",
        "desc": "Mira and Dev work through the project control path on the same display: a constant-time-gap PID base, one of seven tabular Q residual actions, a proposed acceleration, a simplified stopping-margin check, and the point-mass vehicle model.",
        "cuts": [
            ("5s", "Wide Shot / Two-Shot, 84° FOV, Camera Crane Up", "Begin with both seated at the flow diagram. Mira points to the CTG-PID base; Dev traces the arrow toward the Q table. The camera rises only enough to reveal the complete left-to-right control path. Their eyes stay on the same node."),
            ("4s", "Extreme Close-Up, 18° FOV, Camera Dolly In", "A small Q-table tile resolves into seven violet action marks beside a teal baseline command. Mira moves one marker onto the proposed-action line; Dev keeps the red pencil just below it. Simple luminous blocks, crisp surfaces and one clear action."),
            ("6s", "Medium Shot, 63° FOV, Camera Arc", "Dev checks the braking-margin box and points to the command it permits; Mira follows the arrow to the vehicle-model block and nods only after checking the label area. Keep all labels abstract for post graphics. Hold their shared attention on the guarded command."),
        ],
    },
    {
        "title": "Train, then hold out",
        "desc": "The display divides the experiment into training profiles and held-out evaluation cases. Mira presents the training coverage; Dev checks that the cut-in and emergency-braking cases were not used to train Q-learning.",
        "cuts": [
            ("5s", "Medium Shot, 47° FOV, Camera Dolly In", "Mira advances one compact training counter from its first tick toward a full row of 6,000 episode marks. Three colored tracks represent steady, wave and moderate-braking profiles. Dev watches the count, then moves his pencil to the evaluation side."),
            ("5s", "Overhead Shot, 18° FOV, Camera Crane Over The Head", "A tidy matrix shows four controller lanes crossed with five scenario families and repeated seed dots. The held-out cut-in and emergency cases are amber. Mira marks one shared seed across lanes; Dev checks the alignment. Exact labels are composited in post."),
            ("5s", "Two-Shot, 63° FOV, Camera Arc", "The camera arcs to reveal both students and the full matched-seed matrix. Mira opens her palm toward the same-seed row; Dev places his red pencil across the row as a fairness marker, then looks to her. A quiet, deliberate pause."),
        ],
    },
    {
        "title": "Without guard / with guard",
        "desc": "The display presents two aligned copies of representative seed 17 from the synthetic cut-in episode: Q-learning without the guard and Q-learning with the simplified guard. Keep the graph blank of generated text; the actual CSV trace and aggregate numbers are overlaid in the final edit.",
        "cuts": [
            ("4s", "Wide Shot / Two-Shot, 84° FOV, Camera Crane Up", "Two empty gap-trace panels appear side by side on the monitor. Mira stands at the left panel and Dev at the right; each follows the same vertical event marker. A thin violet line and a thin teal line draw from the same start point."),
            ("4s", "Insert Shot, 12° FOV, Camera Dolly In", "The event marker crosses both charts at once. Mira's violet trace moves closer to the lower plot boundary; Dev's teal trace holds farther from it. These are schematic placeholders for post-edited real data; all plotted motion stays smooth and physically legible."),
            ("7s", "Medium Close-Up / Two-Shot, 47° FOV, Camera Arc", "Hold the split result for seven seconds. Mira looks from the 7.00 metre card to the 11.35 metre card; Dev keeps his pencil at the shared-seed label, then gives one restrained nod. Their faces register that the guard helps gap measures. This is the hero evidence hold; reserve clear screen space for exact metrics added in post."),
        ],
    },
    {
        "title": "The comfort cost and the MPC reference",
        "desc": "The full four-controller cut-in summary appears as three aligned metric columns: mean episode minimum gap, mean share of closing samples with TTC below two seconds, and mean absolute jerk. The jerk result complicates the improvement.",
        "cuts": [
            ("5s", "Medium Close-Up, 47° FOV, Camera Dolly In", "Mira traces the minimum-gap column as the Q-plus-guard bar reaches 11.35 metres. Dev's gaze shifts to the jerk column before his pencil touches the screen edge. The camera stays with their evidence-reading behavior, not an exaggerated reaction."),
            ("5s", "Extreme Close-Up, 18° FOV, Camera Crane Down", "Dev's pencil lands once beside the jerk comparison: 0.96 to 1.22 metres per second cubed. Mira's pencil stops, then moves back to the gap row. A violet mark identifies Q-learning, teal identifies Q plus guard, amber identifies MPC; exact text is composited in the edit."),
            ("5s", "Wide Shot / Two-Shot, 84° FOV, Camera Dolly Left", "Reveal the full benchmark panel. The MPC row extends to 13.11 metres, carries a zero low-TTC share, and shows lower mean absolute jerk at 0.63. Dev lowers his pencil; Mira turns the display toward the audience. Keep all four controller rows visible and equally legible."),
        ],
    },
    {
        "title": "What the simulation can claim",
        "desc": "Mira and Dev arrive at a measured conclusion in the same lab. They agree on the guard's observed gap benefit and jerk cost, disclose the model's limits, and choose measured cut-in replay as the next step.",
        "cuts": [
            ("5s", "Wide Shot / Two-Shot, 84° FOV, Camera Crane Up", "The camera rises from the experiment matrix to both students standing beside the display. Mira closes the notebook only after Dev points to the limitations card. They face the same screen, aligned as teammates rather than opposing sides."),
            ("4s", "Medium Close-Up, 47° FOV, Camera Arc", "Dev points once to a simple one-dimensional model sketch and the phrase area reserved for the next-step card. Mira listens with active eyes, takes one quiet breath, then turns the card toward him. Their disagreement has become a shared plan."),
            ("6s", "Wide Shot / Two-Shot, 84° FOV, Camera Dolly Out", "Both place their pencils beside the next-step card for measured cut-in replay with lane geometry and sensing. The monitor settles on a clean closing plate with open space for the final title: a class simulation, no production-car comparison, no safety proof. Hold the last frame steadily."),
        ],
    },
]


def full_prompt(scene: dict) -> str:
    lines = [
        STYLE_PREFIX,
        "",
        "Characters:",
        f"@Image1: Mira character identity reference, full-preserve; 100% matches the reference. {MIRA}",
        f"@Image2: Dev character identity reference, full-preserve; 100% matches the reference. {DEV}",
        f"@Image3: lab environment reference, full-preserve. {ENV}",
        "Both characters remain in the lab for this scene; screen inserts keep their hands or silhouettes present at the edge of frame.",
        "",
        "Scene:",
        scene["desc"],
        "",
    ]
    for i, (length, shot, action) in enumerate(scene["cuts"], start=1):
        lines.append(f"CUT {i} — {length} · {shot}:")
        lines.append(action)
        lines.append("")
    lines.extend([
        "AUDIO:",
        "Diegetic sound only: quiet ventilation and one soft pencil or interface tap tied to the visible action. Characters remain silent; narration and score are added in post. NO BGM.",
        "",
        "POSITIVE LOCKS:",
        "Anatomically correct, all limbs visible and naturally positioned. Faces, heights, hair, clothing, desk and monitor geometry match the attached references across every cut. Screen graphics are flat abstract shapes; exact text, numbers and data are added in the final edit. Cuts occur only at the specified points; the camera does not cut on its own.",
    ])
    return "\n".join(lines)


def scene_html(index: int, scene: dict) -> str:
    prompt = escape(full_prompt(scene))
    return f"""<article class="scene" data-scene="{index}">
  <div class="scene-head">
    <label class="done"><input type="checkbox" data-scene="{index}"> <span>{index:02d}</span></label>
    <div><h2>{escape(scene['title'])}</h2><p>{escape(scene['desc'])}</p></div>
    <div class="spec">Seedance 2.0 · Standard · 15s · 16:9 · 1080p</div>
  </div>
  <div class="prompt-top"><span>Reference-based clip · {sum(float(c[0][:-1]) for c in scene['cuts']):.0f}s cut budget</span><button class="copy">Copy full prompt</button></div>
  <pre class="prompt">{prompt}</pre>
</article>"""


def build_html() -> str:
    scenes = "\n".join(scene_html(i, scene) for i, scene in enumerate(SCENES, start=1))
    prefix = escape(STYLE_PREFIX)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ACC Cut-in Film — Higgsfield Director's Shotlist</title>
<style>
:root{{--bg:#08111d;--panel:#101f31;--panel2:#15263a;--border:#2a4058;--text:#eff5fa;--muted:#a4b4c6;--dim:#74879c;--teal:#4ddccd;--amber:#ffbe69;--violet:#b697ff;--green:#7be2a9}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 78% 8%,#102a3b 0,transparent 38%),var(--bg);color:var(--text);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;padding:34px 22px 72px}}
.wrap{{max-width:1120px;margin:auto}}header{{display:flex;justify-content:space-between;gap:24px;align-items:flex-end;border-bottom:1px solid var(--border);padding:0 0 24px;margin-bottom:24px}}h1{{font-size:34px;line-height:1.12;margin:0 0 8px;letter-spacing:-.03em}}.lede{{color:var(--muted);max-width:720px;margin:0}}.badge{{color:var(--teal);font:12px ui-monospace,monospace;letter-spacing:.08em;border:1px solid #2e726f;border-radius:999px;padding:8px 12px;white-space:nowrap}}
.card,.scene{{background:linear-gradient(155deg,#112239,#0e1a2a 70%);border:1px solid var(--border);border-radius:16px;margin:18px 0;padding:22px}}
h2{{font-size:21px;margin:0 0 3px;letter-spacing:-.01em}}h3{{font-size:15px;text-transform:uppercase;letter-spacing:.08em;color:var(--teal);margin:0 0 10px}}p{{margin:6px 0;color:var(--muted)}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}.asset{{background:#0a1625;border:1px solid #25394f;border-radius:11px;padding:12px}}.asset b{{color:var(--text)}}.asset code{{color:var(--amber)}}
details{{background:#0a1726;border:1px solid #2a4058;border-radius:12px;padding:14px 16px;margin-top:14px}}summary{{cursor:pointer;color:var(--teal);font-weight:650}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;color:#cbd9e7;margin:12px 0 0}}.note{{border-left:3px solid var(--amber);padding:4px 0 4px 14px;color:#d7e1eb;margin:14px 0}}
.scene-head{{display:grid;grid-template-columns:58px 1fr auto;gap:15px;align-items:start}}.done{{display:flex;align-items:center;gap:8px;color:var(--amber);font:13px ui-monospace,monospace;padding-top:5px}}input[type=checkbox]{{accent-color:#4ddccd;width:16px;height:16px}}.spec{{font:11px ui-monospace,monospace;color:var(--teal);border:1px solid #2c6767;border-radius:8px;padding:7px 9px;white-space:nowrap}}.prompt-top{{display:flex;justify-content:space-between;align-items:center;color:var(--dim);font:11px ui-monospace,monospace;margin:18px 0 0;padding:10px 12px;background:#0a1725;border:1px solid var(--border);border-bottom:0;border-radius:10px 10px 0 0}}button{{background:transparent;border:1px solid #477d7a;color:var(--teal);border-radius:7px;padding:6px 10px;font:12px ui-monospace,monospace;cursor:pointer}}button:hover,button.copied{{background:#153d3b}}.prompt{{background:#091421;border:1px solid var(--border);border-radius:0 0 10px 10px;padding:16px;color:#d0deea}}.scene.done h2{{color:#9aabba}}.legend{{display:flex;gap:18px;flex-wrap:wrap;color:var(--muted);font:12px ui-monospace,monospace}}.legend span::before{{content:"";display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;background:var(--teal)}}.legend span:nth-child(2)::before{{background:var(--violet)}}.legend span:nth-child(3)::before{{background:var(--amber)}}
@media(max-width:760px){{header{{display:block}}.badge{{display:inline-block;margin-top:16px}}.grid{{grid-template-columns:1fr}}.scene-head{{grid-template-columns:42px 1fr}}.spec{{grid-column:2;justify-self:start;white-space:normal}}.card,.scene{{padding:16px}}}}
</style></head><body><main class="wrap">
<header><div><div class="badge">AUTOMOTIVE TECHNOLOGY · PROJECT FILM</div><h1>When the Gap Shrinks</h1><p class="lede">A 105-second, seven-clip Higgsfield plan for a character-led explanation of the ACC project: why it matters, how the small Q-learning correction and braking guard work, the result without and with the guard, the comfort trade-off, and the simulation's limits.</p></div><div class="badge">SEEDANCE 2.0 · 7 × 15s</div></header>

<section class="card"><h3>Before generating</h3><p>Use <b>Reference-based</b> mode. Set every clip to <b>Seedance 2.0 · Standard · 15 seconds · 16:9 · 1080p</b>. Attach the supplied reference images in the same order each time; then copy one scene prompt below. Use the closing MP4 as a data-accurate edit reference. Exact labels and numbers belong in post-edit graphics because generated screen text is unreliable.</p>
<div class="grid" style="margin-top:14px"><div class="asset"><b><code>@Image1</code> / Mira</b><p>Upload <code>Mira_Character_Reference.png</code> first; character identity, full-preserve.</p></div><div class="asset"><b><code>@Image2</code> / Dev</b><p>Upload <code>Dev_Character_Reference.png</code> second; character identity, full-preserve.</p></div><div class="asset"><b><code>@Image3</code> / lab</b><p>Upload <code>ACC_Lab_Environment_Reference.png</code> third; environment geometry and light, full-preserve.</p></div></div>
<p class="note">Keep the exact comparison attached in the final edit: Q without guard 7.00 m / 2.04% / 0.96 m/s³; Q with the simplified guard 11.35 m / 0.00% / 1.22 m/s³; MPC 13.11 m / 0.00% / 0.63 m/s³. Values are means from 50 matched synthetic cut-in episodes. The guard is simplified and RSS-inspired; it is not formal RSS.</p>
<details><summary>Global Style Prefix — copied into every scene prompt</summary><pre>{prefix}</pre></details></section>

<section class="card"><h3>Asset glossary</h3><div class="grid"><div class="asset"><b>@Image1 — Mira</b><p>Character identity reference. 165 cm, warm-brown skin, straight black shoulder-length bob with left part, compact build, teal crewneck, orange lanyard, dark trousers.</p></div><div class="asset"><b>@Image2 — Dev</b><p>Character identity reference. 178 cm, deep-brown skin, short textured black curls, round dark glasses, tall lean build, indigo work shirt with amber cuff, red mechanical pencil.</p></div><div class="asset"><b>@Image3 — ACC lab</b><p>One matte-display automotive-controls lab after dusk; charcoal workbench, one desk lamp, two stools. Same room in every clip.</p></div></div><div class="legend" style="margin-top:16px"><span>Teal · controlled/guarded path</span><span>Violet · learned correction</span><span>Amber · test event/benchmark</span></div></section>

<section><h3 style="margin:28px 4px 12px">Connected director's shotlist</h3>{scenes}</section>
<section class="card"><h3>Final edit order</h3><p>Place clips 01–07 in order. Add one continuous voiceover, quiet lab ambience, and a restrained original underscore. Overlay the provided matched-run charts and labels; keep the phrase “instantaneous gap-step proxy” visible when the test event appears. Finish with the one-dimensional model limits and “class simulation — not a safety proof or production-car comparison.” Captions are supplied as an SRT beside the local explainer video.</p></section>
<script>
document.querySelectorAll('input[type=checkbox]').forEach(cb=>{{const key='acc-shot-'+cb.dataset.scene;cb.checked=localStorage.getItem(key)==='1';cb.addEventListener('change',()=>{{localStorage.setItem(key,cb.checked?'1':'0');cb.closest('.scene').classList.toggle('done',cb.checked)}});if(cb.checked)cb.closest('.scene').classList.add('done')}});
document.querySelectorAll('button.copy').forEach(btn=>btn.addEventListener('click',async()=>{{const p=btn.closest('.scene').querySelector('pre.prompt');await navigator.clipboard.writeText(p.textContent);const old=btn.textContent;btn.textContent='Copied';btn.classList.add('copied');setTimeout(()=>{{btn.textContent=old;btn.classList.remove('copied')}},1300)}}));
</script></main></body></html>"""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_html(), encoding="utf-8")
    print(f"Wrote {OUT} · {len(SCENES)} clips · 15 seconds each · 16:9 · 1080p")


if __name__ == "__main__":
    main()
