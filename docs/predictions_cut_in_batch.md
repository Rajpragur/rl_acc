# Pre-run predictions: randomized cut-in evaluation

Written before the expanded batch run on 16 October 2026.

## Question

Across matched randomized synthetic cut-in episodes, does an RSS-inspired braking-distance guard improve the unfiltered tabular Q policy's short-time-to-collision exposure and minimum gap, and what does that cost in smoothness and tracking?

## Protocol locked before running

- 50 seeds per scenario-controller cell; each seed supplies the same initial conditions and event parameters to all four controllers.
- Cut-in onset 6–10 s; instantaneous gap reduction 16–26 m; lead braking 3.5–5.0 m/s² for 2–3 s.
- Five scenario families total: steady, wave, moderate brake, synthetic cut-in holdout, and higher-speed emergency-brake holdout.
- Four controllers: CTG-PID, simplified MPC, residual tabular Q, residual Q plus the guard.
- Primary cut-in measures: minimum gap, percentage of closing samples with TTC below 2 s, collision indicator, mean absolute jerk, and gap RMSE.
- Report episode means and approximate 95% intervals; for controller comparisons, use paired per-seed differences. These intervals are descriptive and are not significance tests.

## Predictions

1. Q plus guard will reduce Q's short-TTC exposure and improve minimum gap in the cut-in family.
2. The guard will intervene more often in cut-ins than in training-like scenarios and will increase jerk relative to Q.
3. MPC will have lower cut-in gap RMSE than Q; CTG-PID will have lower mean absolute jerk than Q.
4. No result will be interpreted as evidence that the project outperforms a production ACC vehicle. Commercial controls are proprietary and the available OpenACC sample is not a matched cut-in trial.

## Scope

The cut-in is a longitudinal distance step with no lateral vehicle path or perception model. A favorable result would apply only to this randomized simulator family and the stated point-mass assumptions.
