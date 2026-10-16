# Predictions recorded before the controller runs

Prepared 16 October 2026, before the full controller comparison.

| Measure | Prediction | Reason |
|---|---|---|
| Gap tracking | MPC will have the lowest in-distribution gap RMSE; CTG-PID will be close in steady following; tabular Q-learning will show a larger error because its actions are discrete. | MPC minimizes a receding-horizon spacing cost. Q-learning has a coarse state and action grid. |
| Comfort | CTG-PID will be smoothest in steady following. Q-learning may show larger jerk because it selects among fixed acceleration levels. | The learned policy has no continuous action interpolation. |
| Holdout cut-in and emergency braking | The unfiltered learner will lose more performance than its in-distribution result. | The holdout profiles are outside its training set. |
| Safety filter | The RSS-inspired guard will increase interventions and reduce unsafe stopping-margin commands. It may increase jerk and gap error. | The guard can replace a comfort-oriented action with stronger braking near the stopping envelope. |
| Runtime | The learned action lookup and CTG-PID will be much faster than grid-search MPC. | MPC evaluates several candidate commands over a short horizon at every control step. |
| Platoon wave test | No controller is assumed string-stable in advance. | Stability depends on the controller, the chosen time gap, actuator lag, and the disturbance profile. |

These are hypotheses, not results. We keep this page unchanged after running the experiments and discuss any mismatch in the report.
