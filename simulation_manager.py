from algorithms_env import AlgorithmsEnv
from blue_object import BlueObject
from red_object import RedObject
import numpy as np


class SimulationManager:
    def __init__(self, red_object_list: list[RedObject], blue_object_list: [BlueObject]):
        self.env: AlgorithmsEnv = AlgorithmsEnv(red_object_list, blue_object_list)
        self.time: int = 0

    def run_simulation(self):
        for idx in range(1000):
            action = self.env.action_space.sample()
            observation, reward, terminated, info, _ = self.env.step(action)

            if terminated:
                self.env.reset()

            # print the reward
            if idx % 100 == 0:
                print(f"Step: {idx}, Reward: {reward}")

    def kill_manager(self):
        # check if there is blue object that is near red object, if so, kill the both
        for blue_object in self.env.blue_object_list:
            for red_object in self.env.red_object_list:
                if np.linalg.norm(blue_object.position - red_object.position) < 1:
                    blue_object.i_am_alive = False
                    red_object.i_am_alive = False

    def step(self, action):
        self.time += 1
        self.kill_manager()
        obs, reward, done, info, _ = self.env.step(action)

        return obs, reward, done, _

    def reset(self):
        self.time = 0
        self.env.reset()
