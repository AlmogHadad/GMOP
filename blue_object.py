import numpy as np


class BlueObject:
    def __init__(self,
                 blue_id: int = -1,
                 launch_site_position: np.ndarray = np.array([0, 0, 0], dtype=np.float64),
                 max_speed: float = 3):
        self.id = blue_id
        self.launch_site_position = launch_site_position.copy()
        self.position = launch_site_position.copy()
        self.max_speed = max_speed

    def step(self, action):
        # Calculate the direction vector from the interceptor to the target
        action = action.astype(np.float64)

        # Normalize the direction vector
        distance = np.linalg.norm(action)
        if distance == 0:
            return self.position

        # Scale the action to move a maximum of 3 units in each direction
        action = (action / distance) * min(self.max_speed, distance)

        self.position += action
        return self.position

    def reset(self):
        print(f'lanch site position: {self.launch_site_position}')
        print(f'before position: {self.position}')
        self.position = self.launch_site_position.copy()
        print(f'after position: {self.position}')
        return self.position

    def get_obs(self):
        return self.position