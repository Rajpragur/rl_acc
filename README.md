# Adaptive cruise control with a small Q-learning correction

This course project studies a specific question: **can a simple braking-distance guard help a tabular Q-learning ACC controller respond to a sudden cut-in?** The learned policy adds one of seven discrete acceleration corrections to a constant-time-gap PID controller. It is intentionally small enough to inspect and run on a laptop CPU.

## Main result

The randomized simulation evaluated four controllers over 1,000 matched episodes (50 seeds for each of five scenario families and four controllers). In the 50 synthetic cut-in runs, adding the guard to Q-learning raised mean episode minimum gap from 7.00 m to 11.35 m and reduced the measured share of closing samples with time-to-collision below two seconds from 2.04% to zero. It also increased mean absolute jerk from 0.957 to 1.222 m/s³. Simplified MPC had the largest mean minimum gap (13.11 m) and lowest cut-in gap RMSE (3.76 m). These are model results, not road-safety evidence; the simulated cut-in is an instantaneous longitudinal gap drop, with no lane-change or perception model.

## Deliverables

- Presentation: `output/ACC_RL_CutIn_Focused_Presentation.pptx`
- Project and literature-review handbook: `output/ACC_RL_Project_Guide.pdf`
- Short learning guide: [`output/pdf/ACC_RL_Learning_Guide.pdf`](output/pdf/ACC_RL_Learning_Guide.pdf), with a code map, controller explanation, Q-learning walkthrough, simulation settings, evaluation protocol, and results-reading notes. Rebuild it with `python src/make_learning_guide.py`.
- Matched episode metrics, summaries, intervals, manifest and representative traces: `outputs/formal_50seed/`
- Three same-seed cut-in comparison clips: `outputs/formal_50seed/ACC_CutIn_Q_Unfiltered.mp4`, `outputs/formal_50seed/ACC_CutIn_Q_RSS_Filtered.mp4` and `outputs/formal_50seed/ACC_CutIn_MPC.mp4`
- Presentation-ready explainer film: `workspace/output/ACC_CutIn_Explainer.mp4` (48 seconds, 1080p, silent, with synchronized trace panels and 50-seed results). Storyboard, optional presenter narration and an imported Higgsfield opener prompt: `workspace/output/ACC_CutIn_Higgsfield_Prompt_and_Voiceover.md`
- Real-world ACC context: the small JRC OpenACC trace in `data/openacc/`, summarized in `outputs/openacc_reference.json`
- Experimental design and iteration notes: `docs/`

## Run the simulation

Python 3.10+ and NumPy are sufficient for training and experiments. Pillow and FFmpeg are needed for MP4 generation. The checked run used a CPU; it does not use GPU, a large neural network or an LLM.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/train_q_learning.py --episodes 6000 --seed 17 --output models/q_agent.npz
python src/run_experiments.py --seeds 50 --output outputs/formal_50seed
```

The official JRC trace can be summarized with:

```sh
python src/analyze_openacc.py
```

Create a video after running the simulation (FFmpeg must be available on `PATH`):

```sh
python src/make_video.py --scenario cut_in --controller Q-Learning \
  --trace outputs/formal_50seed/representative_traces.csv \
  --output outputs/formal_50seed/ACC_CutIn_Q_Unfiltered.mp4

python src/make_explainer_video.py \
  --trace outputs/formal_50seed/representative_traces.csv \
  --summary outputs/formal_50seed/scenario_summary.csv \
  --output workspace/output/ACC_CutIn_Explainer.mp4
```

The explainer renders the Q-Learning, Q+guard and MPC traces from the same representative cut-in episode (seed 17), then reads the aggregate bars from the 50-seed cut-in summary. It labels the event as an instantaneous longitudinal gap step; its graphic does not depict lane-change physics. The end card states that the model has no production ACC head-to-head.

The expanded simulation's measured maximum resident set was about **42 MB** on the project machine. The project uses far less than the available 3–4 GB memory budget.

## Dataset choice

The JRC Open ACC Database is used as descriptive real-road context. The included Vicolungo 2019 sample pairs a human-driven lead car with a Ford S-Max using ACC; it is not a controlled cut-in test and is not a benchmark of every current production system. Dataset attribution and interpretation notes are in `data/openacc/README.md`.

We also reviewed a small U.S. DOT TGSIM I-294 L2 trajectory file and recorded why it was not used as a matched cut-in score benchmark in `data/tgsim/README.md`. The Hugging Face Automingo dataset is image/VQA material rather than longitudinal kinematics and lists a download size of about 21.7 GB, so it was not downloaded. Neither dataset adds a fair ACC cut-in comparison that would justify exceeding the stated memory and download budget.

## Model limits

- The simulator is a one-dimensional point-mass model with a first-order actuator lag.
- The cut-in changes longitudinal gap instantly; it does not simulate lane geometry, sensing, road curvature, grade, weather or driver override.
- The RSS-inspired intervention is a simplified action filter, not a formal RSS implementation, a control barrier certificate or a guarantee.
- The commercial comparison uses an owner manual and a separate OpenACC headway trace. It does not claim that this project beats a current production car.
