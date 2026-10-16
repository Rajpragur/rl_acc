"""Train a transparent tabular Q-learning car-following policy."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from acc_sim import (
    ACTUATOR_TAU, DT, EPISODE_SECONDS, Q_ACTIONS, Q_DIMS,
    lead_acceleration, lead_speed, observation, random_training_setup,
    resistance, rss_braking_margin, q_state_index, select_q_action,
    ctg_pid_action,
)


def train(episodes: int, seed: int) -> tuple[np.ndarray, list[dict]]:
    rng = np.random.default_rng(seed)
    q = np.zeros((*Q_DIMS, len(Q_ACTIONS)), dtype=np.float32)
    alpha = 0.12
    gamma = 0.985
    max_steps = int(EPISODE_SECONDS / DT)
    history: list[dict] = []
    for episode in range(episodes):
        setup = random_training_setup(rng)
        t = 0.0
        gap = setup.initial_gap
        ve = setup.ego_speed
        vl = setup.lead_speed
        actuator = float(resistance(ve))
        last_accel = 0.0
        ep_return = 0.0
        collisions = 0
        epsilon = max(0.05, 1.0 - 0.95 * episode / max(1.0, episodes * 0.8))
        for _ in range(max_steps):
            la = lead_acceleration(setup.scenario, t, setup.lead_base, setup.phase)
            obs = observation(gap, ve, vl, last_accel, la)
            state = q_state_index(obs)
            if rng.random() < epsilon:
                action_idx = int(rng.integers(len(Q_ACTIONS)))
            else:
                action_idx = select_q_action(q[state], obs)
            command = float(np.clip(ctg_pid_action(gap, ve, vl) + Q_ACTIONS[action_idx], -6.0, 2.5))

            vl_next = lead_speed(setup.scenario, t + DT, setup.lead_base, setup.phase)
            actuator += (DT / ACTUATOR_TAU) * (command - actuator)
            accel = actuator - float(resistance(ve))
            ve_next = max(0.0, ve + accel * DT)
            gap_next = gap + 0.5 * (vl + vl_next - ve - ve_next) * DT
            jerk = (accel - last_accel) / DT
            gap_err = gap_next - (5.0 + 1.3 * ve_next)
            closing = ve_next - vl_next
            collision = gap_next <= 0.0
            reward = -0.65 * (gap_err / 20.0) ** 2 - 0.18 * (closing / 8.0) ** 2
            reward -= 0.018 * (accel / 4.0) ** 2 + 0.012 * (jerk / 8.0) ** 2
            # A shaping cost discourages actions that leave little stopping margin.
            margin = rss_braking_margin(gap, ve, vl, command)
            reward -= 0.35 * min(5.0, max(0.0, -margin) / 5.0)
            if collision:
                reward -= 120.0
                collisions += 1

            next_obs = observation(gap_next, ve_next, vl_next, accel,
                                   lead_acceleration(setup.scenario, t + DT,
                                                     setup.lead_base, setup.phase))
            next_state = q_state_index(next_obs)
            target = reward if collision else reward + gamma * float(np.max(q[next_state]))
            q[state + (action_idx,)] += alpha * (target - q[state + (action_idx,)])
            ep_return += reward
            t += DT
            gap, ve, vl, last_accel = gap_next, ve_next, vl_next, accel
            if collision:
                break
        history.append({"episode": episode + 1, "return": ep_return,
                        "epsilon": epsilon, "steps": int(round(t / DT)),
                        "collision": collisions, "profile": setup.scenario})
        if (episode + 1) % 250 == 0 or episode == 0:
            recent = history[-100:]
            avg = float(np.mean([x["return"] for x in recent]))
            print(f"episode {episode + 1:5d}/{episodes}  epsilon={epsilon:.3f}  "
                  f"100-episode return={avg:.1f}  table_states={int(np.count_nonzero(np.max(np.abs(q), axis=-1)))}")
    return q, history


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--output", default="models/q_agent.npz")
    args = parser.parse_args()
    q, history = train(args.episodes, args.seed)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, q_table=q)
    curve_path = path.parent / "training_curve.csv"
    with curve_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(history[0]))
        writer.writeheader()
        writer.writerows(history)
    metadata = {
        "algorithm": "tabular Q-learning",
        "episodes": args.episodes,
        "seed": args.seed,
        "q_table_shape": list(q.shape),
        "state_dimensions": list(Q_DIMS),
        "discrete_residual_actions_mps2_added_to_ctg": [float(a) for a in Q_ACTIONS],
        "nominal_controller": "constant-time-gap feedback",
        "alpha": 0.12,
        "gamma": 0.985,
        "epsilon_schedule": "1.0 to 0.05 over the first 80% of episodes",
        "training_profiles": ["steady", "wave", "moderate brake"],
    }
    path.with_suffix(".json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved Q table to {path}; training log: {curve_path}")


if __name__ == "__main__":
    main()
