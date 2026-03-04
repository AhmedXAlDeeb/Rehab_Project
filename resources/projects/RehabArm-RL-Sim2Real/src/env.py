import gymnasium as gym
from gymnasium import spaces
import mujoco
import numpy as np
import os

class RehabArmEnv(gym.Env):
    def __init__(self, model_path="assets/arm.xml"):
        super().__init__()
        # Robust path handling for Windows
        if not os.path.exists(model_path):
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_path, "assets", "arm.xml")

        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        
        # Actions: Torques for 2 joints (normalized to [-1, 1])
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(2,), dtype=np.float32)
        
        # Observations: [sin(q), cos(q), qvel, target_dist]
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(7,), dtype=np.float32)
        
        self.prev_action = np.zeros(2, dtype=np.float32)
        self.max_steps = 500
        self.current_step = 0

    def _get_obs(self):
        finger_pos = self.data.site_xpos[self.model.site('fingertip').id]
        target_pos = self.data.mocap_pos[0]
        dist_vec = target_pos - finger_pos
        
        return np.concatenate([
            np.sin(self.data.qpos),
            np.cos(self.data.qpos),
            self.data.qvel,
            [np.linalg.norm(dist_vec)]
        ]).astype(np.float32)

    def step(self, action):
        self.current_step += 1
        action = np.asarray(action, dtype=np.float32)
        
        self.data.ctrl[:] = action * 15.0 
        mujoco.mj_step(self.model, self.data)
        
        obs = self._get_obs()
        dist = obs[-1]
        
        # Medical Reward Formula: Distance + Smoothness (Low Jerk) + low Effort
        r_dist = -dist
        r_smooth = -np.square(action - self.prev_action).sum()
        r_effort = -np.square(action).sum()
        
        # Reward weighting prioritized for clinical comfort
        reward = (2.0 * r_dist) + (1.2 * r_smooth) + (0.01 * r_effort)
        
        self.prev_action = action.copy()
        
        terminated = bool(dist < 0.03)
        truncated = bool(self.current_step >= self.max_steps)
        
        return obs, float(reward), terminated, truncated, {"dist": dist}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        mujoco.mj_resetData(self.model, self.data)
        self.current_step = 0
        self.prev_action = np.zeros(2, dtype=np.float32)

        # Domain Randomization: Variation in Mass and Friction
        self.model.body_mass[2] *= np.random.uniform(0.8, 1.2) 
        self.model.body_mass[3] *= np.random.uniform(0.8, 1.2)
        self.model.dof_frictionloss[:] = np.random.uniform(0.01, 0.1, size=2)

        # Randomized Target
        self.data.mocap_pos[0] = np.array([
            np.random.uniform(0.2, 0.5), 
            0, 
            np.random.uniform(0.3, 0.7)
        ])
        
        return self._get_obs(), {}