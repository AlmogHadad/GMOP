import numpy as np

from algorithms_env import AlgorithmsEnv
from blue_object import BlueObject
from red_object import RedObject
import trajectoy_pradiction as tp

class SimulationManager:
    def __init__(self):
        self.env = AlgorithmsEnv()

        self.time = 0
        self.blue_objects: dict[int, BlueObject] = {}
        self.red_objects: dict[int, RedObject] = {}

    def run_simulation(self):
        for idx in range(1000):
            action = self.env.action_space.sample()
            observation, reward, terminated, info, _ = self.env.step(action)

            if terminated:
                self.env.reset()

            # print the reward
            if idx % 100 == 0:
                print(f"Step: {idx}, Reward: {reward}")

    def step(self, action):
        self.time += 1
        obs, reward, done, info, _ = self.env.step(action)
        return obs, reward, done, _

    def reset(self):
        self.time = 0
        self.env.reset()

    def take_action(self):
        # Calculate the direction vector from the interceptor to the target
        red_trajectory_position, red_trajectory_time = tp.red_trajectory_prediction_(self.env.target_position, self.env.target_velocity)
        # choose which trajectory to follow based on the distance

        closest_index = 0
        closest_distance = tp.blue_trajectory_prediction_time(self.env.interceptor_position, 3, red_trajectory_position[0])
        for i in range(1, len(red_trajectory_position)):
            blue_object_prediction_time = tp.blue_trajectory_prediction_time(self.env.interceptor_position, 3, red_trajectory_position[i])
            if closest_distance > abs(blue_object_prediction_time - red_trajectory_time[i]):
                closest_distance = abs(blue_object_prediction_time - red_trajectory_time[i])
                closest_index = i

        action = (red_trajectory_position[closest_index] - self.env.interceptor_position).astype(np.float64)
        # Normalize the direction vector
        distance = np.linalg.norm(action)
        if distance == 0:
            print('Done!')
            return np.zeros_like(action)  # No movement if already at the target

        # Scale the action to move a maximum of 3 units in each direction
        action = (action / distance) * min(3, distance)

        return action
