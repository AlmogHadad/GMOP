import numpy as np


class RedObject:
    def __init__(self,
                 red_id: int = -1,
                 initial_position: np.ndarray = np.array([-50, -50, 50]),
                 velocity: np.ndarray = np.array([1, 0, 0])):
        self.id = red_id
        self.position = initial_position
        self.velocity = velocity

    def step(self):
        self.position += self.velocity
        return self.position

    def reset(self):
        self.position = np.array([-50, -50, 50])
        return self.position

    def get_obs(self):
        return self.position

