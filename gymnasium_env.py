import gymnasium as gym
from gymnasium import spaces
import numpy as np


class UAVInterceptorEnv(gym.Env):
    def __init__(self):
        super(UAVInterceptorEnv, self).__init__()
        self.action_space = spaces.Box(low=-1, high=1, shape=(3,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-100, high=100, shape=(6,), dtype=np.float32)

        self.target_position = np.array([-50, -50, 50])
        self.interceptor_position = np.array([0, 0, 0], dtype=np.float64)
        self.target_velocity = np.array([1, 0, 0])

    def reset(self):
        self.interceptor_position = np.array([0, 0, 0], dtype=np.float64)
        self.target_position = np.array([-50, -50, 50])
        return np.concatenate((self.interceptor_position, self.target_position))

    def step(self, action):
        self.interceptor_position += action
        self.target_position += self.target_velocity
        distance = np.linalg.norm(self.interceptor_position - self.target_position)
        reward = -distance
        done = distance < 1
        return np.concatenate((self.interceptor_position, self.target_position)), reward, done, {}
