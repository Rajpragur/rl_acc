# Historical pre-run predictions: first 8-seed residual-Q comparison

This prediction sheet belongs to the earlier 8-seed evaluation retained in `outputs/`. It is preserved as a record of the first formal protocol. The expanded 50-seed randomized cut-in protocol is recorded in [`predictions_cut_in_batch.md`](predictions_cut_in_batch.md) and is the primary project result.

Prepared 16 October 2026 before the first formal residual-Q run.

| Measure | Prediction | Reason |
|---|---|---|
| Gap tracking | MPC will have the lowest in-distribution RMSE; CTG-PID will be close in steady following; residual Q will have higher error. | MPC optimizes a receding-horizon spacing cost; the Q policy has a coarse state/action grid. |
| Comfort | CTG-PID will have lower jerk than Q. | The learned policy selects among discrete acceleration corrections. |
| Holdout cut-in / emergency braking | Unfiltered Q will lose more performance than in the training-like profiles. | Both stress families are excluded from Q training. |
| Safety filter | The braking-distance guard will reduce unsafe-margin commands but can raise jerk and tracking error. | The guard may replace a comfort-oriented action with stronger braking near its stopping envelope. |
| Runtime | Q lookup and CTG-PID will be faster than grid-search MPC. | MPC evaluates multiple candidate actions over a short horizon at each time step. |
| Platoon pulse | No controller is assumed string-stable in advance. | String response depends on controller, time gap, actuator lag and disturbance profile. |

These are hypotheses, not results. They refer to the original fixed-event 8-seed run only; the later randomized cut-in experiment has its own prediction record.
