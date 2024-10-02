from gymnasium_env import UAVInterceptorEnv
import numpy as np
from blue_object import BlueObject
from red_object import RedObject


class SimulationManager:
    def __init__(self):
        self.env = UAVInterceptorEnv()
        self.env.reset()
        self.blue_objects: dict[int, BlueObject] = {}
        self.red_objects: dict[int, RedObject] = {}
        self.time = 0

    def run_simulation(self):
        for idx in range(1000):
            action = self.env.action_space.sample()
            observation, reward, terminated, info = self.env.step(action)

            if terminated:
                self.env.reset()

            # print the reward
            if idx % 100 == 0:
                print(f"Step: {idx}, Reward: {reward}")

    def step(self, action):
        obs, reward, done, _ = self.env.step(action)
        return obs, reward, done, _

    def reset(self):
        self.time = 0
        self.env.reset()

    def take_action(self):
        # Calculate the direction vector from the interceptor to the target
        action = (self.env.target_position - self.env.interceptor_position).astype(np.float64)

        # Normalize the direction vector
        distance = np.linalg.norm(action)
        if distance == 0:
            return np.zeros_like(action)  # No movement if already at the target

        # Scale the action to move a maximum of 3 units in each direction
        action = (action / distance) * min(3, distance)

        return action
