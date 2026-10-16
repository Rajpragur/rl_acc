"""Compact longitudinal ACC simulation used by the course project.

The model is deliberately transparent: one point-mass ego car follows a scripted
lead car, with bounded command acceleration, a first-order actuator, aerodynamic
drag, and rolling resistance. It is suitable for controller comparison in a
class project, not vehicle certification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
import time
from typing import Any, Callable

import numpy as np


DT = 0.1
EPISODE_SECONDS = 40.0
MAX_STEPS = int(EPISODE_SECONDS / DT)
MASS_KG = 1500.0
RHO_AIR = 1.225
CD_A = 0.62
CRR = 0.012
GRAVITY = 9.81
ACT_MIN = -6.0
ACT_MAX = 2.5
ACTUATOR_TAU = 0.35
STANDSTILL_GAP = 5.0
TIME_GAP = 1.3
TARGET_SPEED = 30.0


def resistance(speed: float | np.ndarray) -> float | np.ndarray:
    """Rolling plus aerodynamic deceleration in m/s^2."""
    return CRR * GRAVITY + 0.5 * RHO_AIR * CD_A * np.asarray(speed) ** 2 / MASS_KG


def desired_gap(speed: float) -> float:
    return STANDSTILL_GAP + TIME_GAP * max(0.0, speed)


def lead_speed(name: str, t: float, base: float = 22.0, phase: float = 0.0,
               parameters: dict[str, float] | None = None) -> float:
    """Scripted leader speed; optional parameters vary each held-out event."""
    p = parameters or {}
    if name == "steady":
        return base
    if name == "wave":
        return max(7.0, base + 2.4 * math.sin(0.22 * t + phase) + 1.1 * math.sin(0.55 * t + phase / 2))
    if name == "brake":
        # Defaults preserve the moderate training profile; holdouts pass varied events.
        start = p.get("event_time_s", 8.0)
        decel = p.get("brake_decel_mps2", 3.0)
        duration = p.get("brake_duration_s", 3.0)
        recovery_start = p.get("recovery_start_s", 18.0)
        recovery_accel = p.get("recovery_accel_mps2", 1.5)
        if t < start:
            return base
        if t < start + duration:
            return max(0.0, base - decel * (t - start))
        plateau = max(0.0, base - decel * duration)
        if t < recovery_start:
            return plateau
        return min(base, plateau + recovery_accel * (t - recovery_start))
    if name == "cut_in":
        start = p.get("event_time_s", 8.0)
        decel = p.get("brake_decel_mps2", 4.0)
        duration = p.get("brake_duration_s", 3.0)
        if t < start:
            return base
        return max(0.0, base - decel * min(duration, t - start))
    if name == "emergency":
        start = p.get("event_time_s", 7.0)
        decel = p.get("brake_decel_mps2", 7.0)
        duration = p.get("brake_duration_s", 2.0)
        if t < start:
            return base
        return max(0.0, base - decel * min(duration, t - start))
    raise ValueError(f"unknown lead profile: {name}")


def lead_acceleration(name: str, t: float, base: float = 22.0, phase: float = 0.0,
                      parameters: dict[str, float] | None = None) -> float:
    """Finite-difference estimate matching the speed profiles."""
    return (lead_speed(name, t + DT, base, phase, parameters)
            - lead_speed(name, t, base, phase, parameters)) / DT


@dataclass
class EpisodeSetup:
    scenario: str
    initial_gap: float
    ego_speed: float
    lead_speed: float
    lead_base: float = 22.0
    phase: float = 0.0
    parameters: dict[str, float] = field(default_factory=dict)


def fixed_setup(scenario: str, seed: int = 0) -> EpisodeSetup:
    rng = np.random.default_rng(seed)
    if scenario == "steady":
        base = float(rng.uniform(20.0, 25.0))
        ego = float(np.clip(base - 4.0 + rng.normal(0.0, 1.0), 12.0, 29.0))
        return EpisodeSetup(scenario, 36.0 + rng.normal(0, 2.0), ego, base, base)
    if scenario == "wave":
        base = float(rng.uniform(20.0, 24.0))
        ego = float(np.clip(base - 2.0 + rng.normal(0.0, 1.0), 12.0, 29.0))
        return EpisodeSetup(scenario, 34.0 + rng.normal(0, 2.0), ego, base, base, rng.uniform(-1.5, 1.5))
    if scenario == "brake":
        base = float(rng.uniform(20.0, 24.0))
        ego = float(np.clip(base - 1.0 + rng.normal(0.0, 1.5), 12.0, 29.0))
        return EpisodeSetup(scenario, 42.0 + rng.normal(0, 2.0), ego, base, base)
    if scenario == "cut_in":
        # Unseen close cut-in with randomized onset, gap reduction and braking.
        base = float(rng.uniform(20.0, 24.0))
        ego = float(np.clip(base - 1.0 + rng.normal(0.0, 1.0), 12.0, 29.0))
        parameters = {
            "event_time_s": float(rng.uniform(6.0, 10.0)),
            "gap_drop_m": float(rng.uniform(16.0, 26.0)),
            "brake_decel_mps2": float(rng.uniform(3.5, 5.0)),
            "brake_duration_s": float(rng.uniform(2.0, 3.0)),
        }
        return EpisodeSetup(scenario, 38.0 + rng.normal(0, 2.5), ego, base, base,
                            parameters=parameters)
    if scenario == "emergency":
        # Higher-speed holdout with randomized onset and severe lead braking.
        base = float(rng.uniform(24.0, 28.0))
        ego = float(np.clip(base + rng.normal(0.0, 1.0), 16.0, 30.0))
        parameters = {
            "event_time_s": float(rng.uniform(5.5, 9.0)),
            "brake_decel_mps2": float(rng.uniform(5.5, 8.0)),
            "brake_duration_s": float(rng.uniform(1.5, 2.4)),
        }
        return EpisodeSetup(scenario, 37.0 + rng.normal(0, 2.5), ego, base, base,
                            parameters=parameters)
    raise ValueError(f"unknown scenario: {scenario}")


def random_training_setup(rng: np.random.Generator) -> EpisodeSetup:
    name = str(rng.choice(["steady", "wave", "brake"], p=[0.2, 0.45, 0.35]))
    base = float(rng.uniform(17.0, 25.0))
    v_ego = float(np.clip(base + rng.normal(0, 2.0), 12.0, 29.0))
    return EpisodeSetup(name, float(rng.uniform(24.0, 55.0)), v_ego, base, base, float(rng.uniform(-1.5, 1.5)))


def rss_braking_margin(gap: float, v_ego: float, v_lead: float, command: float,
                       reaction_time: float = 0.35, ego_brake: float = 6.0,
                       lead_brake: float = 8.0) -> float:
    """RSS-inspired stopping-distance margin under a bounded braking assumption.

    Positive means the proposed command leaves a nonnegative stopping margin under
    this point-mass model. This is an engineering approximation, not a formal RSS
    implementation or a proof against model error.
    """
    net_a = float(command) - float(resistance(v_ego))
    ve_r = max(0.0, v_ego + net_a * reaction_time)
    ego_reaction_distance = v_ego * reaction_time + 0.5 * net_a * reaction_time**2
    vl_r = max(0.0, v_lead - lead_brake * reaction_time)
    lead_reaction_distance = max(0.0, v_lead * reaction_time - 0.5 * lead_brake * reaction_time**2)
    d_ego_brake = ve_r * ve_r / (2.0 * ego_brake)
    d_lead_brake = vl_r * vl_r / (2.0 * lead_brake)
    required = STANDSTILL_GAP + ego_reaction_distance + d_ego_brake - lead_reaction_distance - d_lead_brake
    return gap - max(STANDSTILL_GAP, required)


def safety_filter(gap: float, v_ego: float, v_lead: float, proposed: float) -> tuple[float, bool]:
    """Clip a proposed action to the least-braking command meeting the margin rule."""
    proposed = float(np.clip(proposed, ACT_MIN, ACT_MAX))
    if rss_braking_margin(gap, v_ego, v_lead, proposed) >= 0.0:
        return proposed, False
    # The margin is monotone with command over this bounded action interval.
    lo, hi = ACT_MIN, proposed
    if rss_braking_margin(gap, v_ego, v_lead, lo) < 0.0:
        return ACT_MIN, True
    for _ in range(30):
        mid = 0.5 * (lo + hi)
        if rss_braking_margin(gap, v_ego, v_lead, mid) >= 0.0:
            lo = mid
        else:
            hi = mid
    return lo, True


def observation(gap: float, v_ego: float, v_lead: float, actual_accel: float,
                leader_accel: float) -> np.ndarray:
    gap_err = gap - desired_gap(v_ego)
    return np.asarray([
        np.clip(gap_err / 35.0, -2.0, 2.0),
        np.clip((v_ego - v_lead) / 12.0, -2.0, 2.0),
        np.clip(v_ego / TARGET_SPEED, 0.0, 1.5),
        np.clip(actual_accel / 7.0, -1.0, 1.0),
        np.clip(leader_accel / 8.0, -1.0, 1.0),
    ], dtype=np.float32)


# A compact state table and discrete acceleration set keep every Q-value
# inspectable. Actuator acceleration is included because it carries lag memory.
Q_BINS = [
    np.asarray([-1.0, -0.6, -0.3, -0.1, 0.1, 0.3, 0.6, 1.0]),
    np.asarray([-0.8, -0.5, -0.3, -0.15, 0.0, 0.15, 0.3, 0.5, 0.8]),
    np.asarray([0.25, 0.45, 0.6, 0.75, 0.9, 1.05, 1.2]),
    np.asarray([-0.6, -0.3, -0.1, 0.1, 0.3, 0.6]),
    np.asarray([-0.6, -0.3, -0.1, 0.1, 0.3, 0.6]),
]
Q_DIMS = tuple(len(b) + 1 for b in Q_BINS)
Q_ACTIONS = np.asarray([-1.2, -0.6, -0.25, 0.0, 0.25, 0.6, 1.2], dtype=np.float32)


def q_state_index(obs: np.ndarray) -> tuple[int, ...]:
    return tuple(int(np.searchsorted(edges, float(value), side="right"))
                 for edges, value in zip(Q_BINS, obs))


def select_q_action(q_row: np.ndarray, obs: np.ndarray) -> int:
    """Greedy Q selection with zero-residual tie-breaking for rarely visited bins."""
    top = float(np.max(q_row))
    candidates = np.flatnonzero(np.abs(q_row - top) <= 1e-7)
    if len(candidates) == 1:
        return int(candidates[0])
    return int(candidates[np.argmin(np.abs(Q_ACTIONS[candidates]))])


@dataclass
class QAgent:
    q_table: np.ndarray

    def predict(self, obs: np.ndarray, deterministic: bool = True):
        obs = np.asarray(obs).reshape(-1)
        idx = q_state_index(obs)
        action_idx = select_q_action(self.q_table[idx], obs)
        ve = float(np.clip(obs[2], 0.0, 1.5) * TARGET_SPEED)
        closing = float(obs[1] * 12.0)
        vl = max(0.0, ve - closing)
        gap = desired_gap(ve) + float(obs[0] * 35.0)
        command = ctg_pid_action(gap, ve, vl) + float(Q_ACTIONS[action_idx])
        return np.asarray([np.clip(command, ACT_MIN, ACT_MAX)], dtype=np.float32), None


def ctg_pid_action(gap: float, v_ego: float, v_lead: float) -> float:
    """Constant-time-gap spacing with proportional gap and relative-speed feedback."""
    gap_error = gap - desired_gap(v_ego)
    rel = v_lead - v_ego
    # Small feed-forward term offsets drag at cruise speed.
    return float(np.clip(float(resistance(v_ego)) + 0.10 * gap_error + 0.85 * rel, ACT_MIN, ACT_MAX))


def one_move_mpc_action(gap: float, v_ego: float, v_lead: float, actuator: float,
                        leader_a: float, horizon_steps: int = 18) -> float:
    """One-move, grid-search MPC with a constant-acceleration leader prediction."""
    candidates = np.linspace(ACT_MIN, ACT_MAX, 35, dtype=np.float64)
    v = np.full_like(candidates, v_ego)
    g = np.full_like(candidates, gap)
    u = np.full_like(candidates, actuator)
    a_prev = np.full_like(candidates, actuator - float(resistance(v_ego)))
    score = np.zeros_like(candidates)
    vl = v_lead
    alpha = DT / ACTUATOR_TAU
    for k in range(horizon_steps):
        vl_next = max(0.0, vl + float(np.clip(leader_a, -8.0, 3.0)) * DT)
        u += alpha * (candidates - u)
        a = u - resistance(v)
        v_next = np.maximum(0.0, v + a * DT)
        g += 0.5 * (vl + vl_next - v - v_next) * DT
        err = g - (STANDSTILL_GAP + TIME_GAP * v_next)
        rel = v_next - vl_next
        jerk = (a - a_prev) / DT
        score += 1.0 * (err / 15.0) ** 2 + 0.18 * (rel / 6.0) ** 2
        score += 0.025 * (a / 4.0) ** 2 + 0.004 * (jerk / 8.0) ** 2
        score += 90.0 * np.maximum(0.0, 3.0 - g) ** 2
        a_prev, v, vl = a, v_next, vl_next
    return float(candidates[int(np.argmin(score))])


try:
    import gymnasium as gym
    from gymnasium import spaces

    class ACCGymEnv(gym.Env):
        """Gymnasium environment for PPO training."""
        metadata = {"render_modes": []}

        def __init__(self, seed: int = 0, episode_seconds: float = EPISODE_SECONDS):
            super().__init__()
            self.rng = np.random.default_rng(seed)
            self.episode_seconds = episode_seconds
            self.max_steps = int(episode_seconds / DT)
            self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
            self.observation_space = spaces.Box(low=-2.0, high=2.0, shape=(5,), dtype=np.float32)
            self.setup: EpisodeSetup | None = None
            self.reset(seed=seed)

        def reset(self, *, seed: int | None = None, options: dict | None = None):
            if seed is not None:
                self.rng = np.random.default_rng(seed)
            super().reset(seed=seed)
            self.setup = random_training_setup(self.rng)
            self.t = 0.0
            self.steps = 0
            self.gap = self.setup.initial_gap
            self.v_ego = self.setup.ego_speed
            self.v_lead = self.setup.lead_speed
            self.actuator = float(resistance(self.v_ego))
            self.last_accel = 0.0
            return self._obs(), {}

        def _obs(self) -> np.ndarray:
            assert self.setup is not None
            la = lead_acceleration(self.setup.scenario, self.t, self.setup.lead_base,
                                   self.setup.phase, self.setup.parameters)
            return observation(self.gap, self.v_ego, self.v_lead, self.last_accel, la)

        def step(self, action):
            assert self.setup is not None
            command = ACT_MIN + (float(np.clip(np.asarray(action).reshape(-1)[0], -1, 1)) + 1.0) * 0.5 * (ACT_MAX - ACT_MIN)
            command = float(np.clip(command, ACT_MIN, ACT_MAX))
            la0 = lead_acceleration(self.setup.scenario, self.t, self.setup.lead_base,
                                    self.setup.phase, self.setup.parameters)
            vl_next = lead_speed(self.setup.scenario, self.t + DT, self.setup.lead_base,
                                 self.setup.phase, self.setup.parameters)
            alpha = DT / ACTUATOR_TAU
            self.actuator += alpha * (command - self.actuator)
            accel = self.actuator - float(resistance(self.v_ego))
            ve_next = max(0.0, self.v_ego + accel * DT)
            self.gap += 0.5 * (self.v_lead + vl_next - self.v_ego - ve_next) * DT
            self.t += DT
            self.steps += 1
            jerk = (accel - self.last_accel) / DT
            self.v_ego, self.v_lead, self.last_accel = ve_next, vl_next, accel
            ge = self.gap - desired_gap(self.v_ego)
            closing = max(0.0, self.v_ego - self.v_lead)
            collision = self.gap <= 0.0
            # Automotive objectives dominate the reward. Safety penalty is a soft
            # training signal; the separate evaluation filter is the hard guard.
            reward = -0.65 * (ge / 20.0) ** 2 - 0.18 * ((self.v_ego - self.v_lead) / 8.0) ** 2
            reward -= 0.018 * (accel / 4.0) ** 2 + 0.012 * (jerk / 8.0) ** 2
            reward -= 0.8 * (closing / 8.0) * max(0.0, 10.0 - self.gap) / 10.0
            if collision:
                reward -= 100.0
            terminated = bool(collision)
            truncated = self.steps >= self.max_steps
            info = {"gap": self.gap, "collision": collision, "acceleration": accel}
            return self._obs(), float(reward), terminated, truncated, info

except ImportError:  # Keep analytical baselines importable without optional RL packages.
    ACCGymEnv = None  # type: ignore


def run_episode(controller: str, scenario: str, seed: int = 0, model: Any = None,
                record: bool = False, apply_filter: bool | None = None) -> tuple[dict, list[dict]]:
    """Run one controller/scenario pair and return metrics plus optional trace."""
    setup = fixed_setup(scenario, seed)
    t = 0.0
    steps = 0
    gap, ve, vl = setup.initial_gap, setup.ego_speed, setup.lead_speed
    actuator = float(resistance(ve))
    last_a = 0.0
    initial_gap = gap
    cutin_done = False
    trace: list[dict] = []
    gap_errors: list[float] = []
    jerks: list[float] = []
    ttcs: list[float] = []
    min_gap = float("inf")
    min_rss_margin = float("inf")
    collisions = 0
    interventions = 0
    decision_ms: list[float] = []
    alpha = DT / ACTUATOR_TAU

    if apply_filter is None:
        apply_filter = controller in {"Q+RSS", "CTG-PID+RSS", "MPC+RSS"}

    while steps < MAX_STEPS and gap > 0.0:
        if scenario == "cut_in" and not cutin_done and t >= setup.parameters.get("event_time_s", 8.0):
            gap -= setup.parameters.get("gap_drop_m", 22.0)
            cutin_done = True
        lead_base = setup.lead_base
        la = lead_acceleration(scenario, t, lead_base, setup.phase, setup.parameters)
        start = time.perf_counter()
        if controller in {"CTG-PID", "CTG-PID+RSS"}:
            proposed = ctg_pid_action(gap, ve, vl)
        elif controller in {"MPC", "MPC+RSS"}:
            proposed = one_move_mpc_action(gap, ve, vl, actuator, la)
        elif controller in {"Q-Learning", "Q+RSS"}:
            if model is None:
                raise ValueError("a trained Q-learning policy is required")
            obs = observation(gap, ve, vl, last_a, la)
            action, _ = model.predict(obs, deterministic=True)
            proposed = float(np.clip(np.asarray(action).reshape(-1)[0], ACT_MIN, ACT_MAX))
        else:
            raise ValueError(f"unknown controller: {controller}")
        command = float(np.clip(proposed, ACT_MIN, ACT_MAX))
        if apply_filter:
            command, intervened = safety_filter(gap, ve, vl, command)
            interventions += int(intervened)
        decision_ms.append((time.perf_counter() - start) * 1000.0)

        rss_m = rss_braking_margin(gap, ve, vl, command)
        min_rss_margin = min(min_rss_margin, rss_m)
        vl_next = lead_speed(scenario, t + DT, lead_base, setup.phase, setup.parameters)
        actuator += alpha * (command - actuator)
        accel = actuator - float(resistance(ve))
        ve_next = max(0.0, ve + accel * DT)
        gap_next = gap + 0.5 * (vl + vl_next - ve - ve_next) * DT
        jerk = (accel - last_a) / DT
        gap_error = gap - desired_gap(ve)
        closing = ve - vl
        if closing > 0.1:
            ttcs.append(max(0.0, gap) / closing)
        min_gap = min(min_gap, gap)
        gap_errors.append(gap_error)
        jerks.append(jerk)
        if record:
            trace.append({
                "t": t, "gap": gap, "desired_gap": desired_gap(ve), "ego_speed": ve,
                "lead_speed": vl, "command": command, "proposed": proposed,
                "acceleration": accel, "jerk": jerk,
                "rss_margin": rss_m, "intervention": int(command < proposed - 1e-5),
                "event_time_s": setup.parameters.get("event_time_s", float("nan")),
                "gap_drop_m": setup.parameters.get("gap_drop_m", float("nan")),
                "brake_decel_mps2": setup.parameters.get("brake_decel_mps2", float("nan")),
            })
        t += DT
        steps += 1
        gap, ve, vl, last_a = gap_next, ve_next, vl_next, accel
    if gap <= 0:
        collisions = 1
    min_ttc = float(np.min(ttcs)) if ttcs else float("nan")
    result = {
        "controller": controller,
        "scenario": scenario,
        "seed": seed,
        "duration_s": round(steps * DT, 2),
        "gap_rmse_m": float(np.sqrt(np.mean(np.square(gap_errors)))) if gap_errors else float("nan"),
        "mean_abs_jerk_mps3": float(np.mean(np.abs(jerks))) if jerks else float("nan"),
        "rms_jerk_mps3": float(np.sqrt(np.mean(np.square(jerks)))) if jerks else float("nan"),
        "min_ttc_s": min_ttc,
        "ttc_below_2s_pct": float(100.0 * np.mean(np.asarray(ttcs) < 2.0)) if ttcs else 0.0,
        "min_gap_m": float(min_gap),
        "collision": collisions,
        "rss_interventions": interventions,
        "rss_intervention_pct": 100.0 * interventions / max(1, steps),
        "min_command_margin_m": float(min_rss_margin),
        "mean_decision_ms": float(np.mean(decision_ms)) if decision_ms else float("nan"),
        "steps": steps,
        "initial_gap_m": initial_gap,
        "scenario_event_time_s": setup.parameters.get("event_time_s", float("nan")),
        "scenario_gap_drop_m": setup.parameters.get("gap_drop_m", float("nan")),
        "scenario_brake_decel_mps2": setup.parameters.get("brake_decel_mps2", float("nan")),
        "scenario_brake_duration_s": setup.parameters.get("brake_duration_s", float("nan")),
    }
    return result, trace


def string_stability_test(controller: str, model: Any = None, vehicles: int = 4,
                          duration_s: float = 32.0) -> dict:
    """Small homogeneous platoon test; ratio is peak speed deviation at last follower
    divided by the leader's peak deviation from the initial speed.
    """
    nsteps = int(duration_s / DT)
    speeds = np.full(vehicles, 22.0, dtype=np.float64)
    positions = np.arange(vehicles, dtype=np.float64) * -34.0
    actuator_state = np.full(vehicles, float(resistance(22.0)), dtype=np.float64)
    actual_a = np.zeros(vehicles, dtype=np.float64)
    histories = np.zeros((nsteps, vehicles), dtype=np.float64)
    interv = 0
    alpha = DT / ACTUATOR_TAU
    for k in range(nsteps):
        t = k * DT
        lead_a = -2.0 if 8.0 <= t < 9.2 else (2.0 if 12.0 <= t < 13.2 else 0.0)
        old_v0 = speeds[0]
        new_v0 = max(0.0, old_v0 + lead_a * DT)
        positions[0] += 0.5 * (old_v0 + new_v0) * DT
        speeds[0] = new_v0
        actual_a[0] = lead_a
        for i in range(1, vehicles):
            gap = positions[i - 1] - positions[i]
            la = actual_a[i - 1]
            if controller in {"CTG-PID", "CTG-PID+RSS"}:
                proposed = ctg_pid_action(gap, speeds[i], speeds[i - 1])
            elif controller in {"MPC", "MPC+RSS"}:
                proposed = one_move_mpc_action(gap, speeds[i], speeds[i - 1], actuator_state[i], la, 12)
            elif controller in {"Q-Learning", "Q+RSS"}:
                obs = observation(gap, speeds[i], speeds[i - 1], actual_a[i], la)
                action, _ = model.predict(obs, deterministic=True)
                proposed = float(np.asarray(action).reshape(-1)[0])
            else:
                raise ValueError(controller)
            use_filter = controller.endswith("+RSS")
            if use_filter:
                command, changed = safety_filter(gap, speeds[i], speeds[i - 1], proposed)
                interv += int(changed)
            else:
                command = float(np.clip(proposed, ACT_MIN, ACT_MAX))
            command = float(np.clip(command, ACT_MIN, ACT_MAX))
            old_vi = speeds[i]
            actuator_state[i] += alpha * (command - actuator_state[i])
            ai = actuator_state[i] - float(resistance(old_vi))
            new_vi = max(0.0, old_vi + ai * DT)
            positions[i] += 0.5 * (old_vi + new_vi) * DT
            speeds[i] = new_vi
            actual_a[i] = ai
        histories[k] = speeds
    peak = np.max(np.abs(histories - 22.0), axis=0)
    leader_peak = max(peak[0], 1e-6)
    ratio = float(peak[-1] / leader_peak)
    return {"controller": controller, "leader_peak_mps": float(leader_peak),
            "last_follower_peak_mps": float(peak[-1]), "amplification_ratio": ratio,
            "string_stable_under_test": bool(ratio <= 1.0), "filter_interventions": interv,
            "vehicle_count": vehicles, "duration_s": duration_s}
