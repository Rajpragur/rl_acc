# Controller design log

## Direct-action Q pilot

The first version let tabular Q-learning choose absolute acceleration directly. In the matched five-scenario pilot (8 seeds per cell, 160 episodes), it performed poorly: its in-distribution gap RMSE was 15.20 m versus 2.36 m for CTG-PID and 1.58 m for MPC. The unfiltered policy collided in 1 of 24 in-distribution episodes and amplified the selected four-car speed disturbance by a factor of 5.70. Adding the RSS-inspired filter removed collisions in this small sample, but gap RMSE rose to 20.09 m. These pilot files are preserved under `outputs/pilot_absolute_q/`.

## Residual-Q revision

The learned action now adds one of seven small acceleration corrections to the CTG-PID command. For tied or unvisited state bins, the policy selects a zero correction. This gives the policy a classical fallback while allowing Q-learning to adjust behavior where it has learned a value difference.

The formal run evaluates the revised policy from a newly trained table. Its metrics are kept separate from the pilot. The change does not make the filter or the policy formally safe; it makes the baseline contribution explicit and testable.
