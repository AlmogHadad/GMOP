import numpy as np


def trajectory_prediction_position_velocity(red_object_position, red_object_velocity, red_type: str = 'CM', steps: int = 30) -> tuple[list[int], list[int]]:
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


def trajectory_prediction_to_target(blue_object_position, blue_object_max_speed, target_position):
    # return in what time the blue object will reach the target
    distance = np.linalg.norm(target_position - blue_object_position)
    return distance / blue_object_max_speed

