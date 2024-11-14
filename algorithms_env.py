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


    def step(self, action):
        # red object step
        for red_object in self.red_object_list:
            red_object.step()

        # blue object step
        for idx, blue_object in enumerate(self.blue_object_list):
            blue_object.step(action[idx])

        # check if there is objects alive
        done = True
        for red_object in self.red_object_list:
            if red_object.i_am_alive:
                done = False
                break

        return np.concatenate((self.blue_object_list[0].position, self.red_object_list[0].position)), 0, done, {}, {}

    def take_action(self):
        actions = []
        red_object_list, blue_object_list = reorder_objects_by_distance(self.red_object_list, self.blue_object_list)

        num_objects = min(len(red_object_list), len(blue_object_list))

        for i in range(num_objects):
            # Predict red trajectory position and time
            red_positions, red_times = tp.trajectory_prediction_position_velocity(
                red_object_list[i].position,
                red_object_list[i].velocity
            )

            # Find the closest red trajectory point based on blue object speed and position
            blue_position = blue_object_list[i].position
            blue_max_speed = blue_object_list[i].max_speed

            closest_index = 0
            closest_distance = tp.trajectory_prediction_to_target(
                blue_position, blue_max_speed, red_positions[0]
            )

            for j, red_pos in enumerate(red_positions[1:], start=1):
                blue_prediction_time = tp.trajectory_prediction_to_target(
                    blue_position, blue_max_speed, red_pos
                )
                distance = abs(blue_prediction_time - red_times[j])

                if distance < closest_distance:
                    closest_distance = distance
                    closest_index = j

            # Calculate the direction vector and append to actions
            action_direction = (red_positions[closest_index] - blue_position).astype(np.float64)
            actions.append(action_direction)

        # Fill remaining actions with zero vectors if blue_object_list is longer
        actions.extend([np.zeros(3, dtype=np.float64)] * (len(blue_object_list) - num_objects))

        return actions


def reorder_objects_by_distance(red_object_list: list[RedObject], blue_object_list: list[BlueObject]) -> tuple[list[RedObject], list[BlueObject]]:
    # Calculate the distance between each red object and blue object
    distances = np.zeros((len(red_object_list), len(blue_object_list)), dtype=np.float64)
    for i, red_object in enumerate(red_object_list):
        for j, blue_object in enumerate(blue_object_list):
            distances[i, j] = np.linalg.norm(red_object.position - blue_object.position)

    # Find the closest red object to each blue object
    red_object_indices = np.argmin(distances, axis=0)
    red_objects = [red_object_list[i] for i in red_object_indices]

    return red_objects, blue_object_list
