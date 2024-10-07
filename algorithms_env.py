# Global Imports
import gymnasium as gym
import numpy as np
from red_object import RedObject
from blue_object import BlueObject
import trajectoy_pradiction as tp


class AlgorithmsEnv(gym.Env):
    def __init__(self, red_object_list: list[RedObject], blue_object_list: list[BlueObject]):
        super(AlgorithmsEnv, self).__init__()

        self.red_object_list: list[RedObject] = red_object_list
        self.blue_object_list: list[BlueObject] = blue_object_list

    def reset(self, **kwargs):
        # reset red object
        for red_object in self.red_object_list:
            red_object.reset()

        # reset blue object
        for blue_object in self.blue_object_list:
            blue_object.reset()

        return np.concatenate((self.blue_object_list[0].position, self.red_object_list[0].position))

    def step(self, action):
        # red object step
        for red_object in self.red_object_list:
            red_object.step()

        # blue object step
        for blue_object in self.blue_object_list:
            blue_object.step(action)

        # check if there is objects alive
        done = True
        for red_object in self.red_object_list:
            if red_object.i_am_alive:
                done = False
                break

        return np.concatenate((self.blue_object_list[0].position, self.red_object_list[0].position)), 0, done, {}, {}

    def take_action(self):
        # Calculate the direction vector from the interceptor to the target
        red_trajectory_position, red_trajectory_time = tp.red_trajectory_prediction(self.red_object_list[0].position,
                                                                                    self.red_object_list[0].velocity)
        # choose which trajectory to follow based on the distance
        closest_index = 0
        closest_distance = tp.blue_trajectory_prediction_time(self.blue_object_list[0].position,
                                                              self.blue_object_list[0].max_speed,
                                                              red_trajectory_position[0])
        # find the closest point in the red trajectory
        for i in range(1, len(red_trajectory_position)):
            blue_object_prediction_time = tp.blue_trajectory_prediction_time(self.blue_object_list[0].position,
                                                                             self.blue_object_list[0].max_speed,
                                                                             red_trajectory_position[i])
            if closest_distance > abs(blue_object_prediction_time - red_trajectory_time[i]):
                closest_distance = abs(blue_object_prediction_time - red_trajectory_time[i])
                closest_index = i

        action = (red_trajectory_position[closest_index] - self.blue_object_list[0].position).astype(np.float64)

        return action