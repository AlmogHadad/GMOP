# Global Imports
import gymnasium as gym
import numpy as np


class AlgorithmsEnv(gym.Env):
    def __init__(self):
        super(AlgorithmsEnv, self).__init__()

        self.target_position = np.array([-50, -50, 50])
        self.interceptor_position = np.array([0, 0, 0], dtype=np.float64)
        self.target_velocity = np.array([1, 0, 0])

    def reset(self, **kwargs):
        self.interceptor_position = np.array([0, 0, 0], dtype=np.float64)
        self.target_position = np.array([-50, -50, 50])
        return np.concatenate((self.interceptor_position, self.target_position))

    def step(self, action):
        # red object step
        self.target_position += self.target_velocity

        # blue object step
        self.interceptor_position += action
        distance = np.linalg.norm(self.interceptor_position - self.target_position)
        reward = -distance
        done = distance < 1

        return np.concatenate((self.interceptor_position, self.target_position)), reward, done, {}, {}
