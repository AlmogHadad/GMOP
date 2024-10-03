import numpy as np
from red_object import RedObject


def red_trajectory_prediction(red_object: RedObject, red_type: str = 'CM', steps: int = 30) -> np.ndarray:
    if red_type == 'CM': # preform linear prediction
        trajectory = np.zeros((steps, 3))
        current_position = red_object.position
        velocity = red_object.velocity
        for i in range(steps):
            trajectory[i] = current_position + velocity
            current_position += velocity
        return trajectory
    else:
        raise ValueError("Invalid Red Type")


def red_trajectory_prediction_(red_object_position, red_object_velocity, red_type: str = 'CM', steps: int = 30) -> tuple[list[int], list[int]]:
    if red_type == 'CM': # preform linear prediction
        trajectory = []
        current_position = red_object_position.copy()
        velocity = red_object_velocity.copy()
        trajectory.append(current_position.copy())
        for i in range(steps-1):
            trajectory.append((current_position + velocity).copy())
            current_position += velocity
        return trajectory, list(range(steps))
    else:
        raise ValueError("Invalid Red Type")


def blue_trajectory_prediction_time(blue_object_position, blue_object_max_speed, target_position):
    # return in what time the blue object will reach the target
    distance = np.linalg.norm(target_position - blue_object_position)
    return distance / blue_object_max_speed

