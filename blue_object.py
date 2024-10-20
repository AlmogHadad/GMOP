import numpy as np
import plotly.graph_objs as go


class BlueObjectBase:
    _id_counter = 1  # Class-level variable to track the unique ID
    def __init__(self,
                 launch_site_position: np.ndarray = np.array([0, 0, 0], dtype=np.float64),
                 max_speed: float = 3):
        self.id = BlueObjectBase._id_counter
        self.launch_site_position = launch_site_position.copy()
        self.position = launch_site_position.copy()
        self.current_velocity = np.array([0, 0, 0], dtype=np.float64)
        self.max_speed = max_speed
        self.i_am_alive = True

        BlueObjectBase._id_counter += 1 # Increment the ID counter

    def step(self, action):
        if self.i_am_alive:
            # Calculate the direction vector from the interceptor to the target
            action = action.astype(np.float64)

            # Normalize the direction vector
            distance = np.linalg.norm(action)
            if distance == 0:
                return self.position

            # Scale the action to move a maximum of 3 units in each direction
            action = (action / distance) * min(self.max_speed, distance)

            self.position += action
            self.current_velocity = action
        return self.position

    def reset(self):
        self.position = self.launch_site_position.copy()
        self.i_am_alive = True

        return self.position

    def get_obs(self):
        return self.position

    def plot_object_3d(self):
        if not self.i_am_alive:
            return go.Scatter3d()
        return go.Scatter3d(x=[self.position[0]], y=[self.position[1]], z=[self.position[2]],
                            mode='markers',
                            marker=dict(size=10, color='blue'),
                            text=f'Blue Object:\n id: {self.id} \n position: {self.position} \n max_speed: {self.max_speed}',
                            showlegend=False)

    def plot_object_2d(self):
        if not self.i_am_alive:
            return go.Scatter()
        return go.Scatter(x=[self.position[0]], y=[self.position[1]],
                          mode='markers',
                          marker=dict(size=10, color='blue'),
                          text=f'Blue Object:\n id: {self.id} \n position: {self.position} \n max_speed: {self.max_speed}',
                          showlegend=False)


    def plot_launch_site_3d(self):
        # make green square for the launch site
        return go.Scatter3d(
            x=[self.launch_site_position[0]],
            y=[self.launch_site_position[1]],
            z=[self.launch_site_position[2]],
            mode='markers',
            marker=dict(size=10, color='green', symbol='square'),  # Use square markers
            text=f'Launch Site: id: {self.id} position: {self.launch_site_position}',
            showlegend=False
        )

    def plot_launch_site_2d(self):
        # make green square for the launch site
        return go.Scatter(
            x=[self.launch_site_position[0]],
            y=[self.launch_site_position[1]],
            mode='markers',
            marker=dict(size=10, color='green', symbol='square'),  # Use square markers
            text=f'Launch Site: id: {self.id} position: {self.launch_site_position}',
            showlegend=False
        )

    def to_dict(self):
        return {
            "position": self.position.tolist(),
            "max_speed": self.max_speed,
        }


class BlueObject(BlueObjectBase):
    def __init__(self,
                 launch_site_position: np.ndarray = np.array([0, 0, 0], dtype=np.float64),
                 max_speed: float = 3):
        super().__init__(launch_site_position, max_speed)

    def step(self, action):
        # TODO: Implement the logic to calculate the next position of the blue object
        super().step(action)

    def reset(self):
        # TODO: Implement the logic to reset the blue object
        super().reset()

    def get_obs(self):
        # TODO: Implement the logic to get the observation of the blue object
        return super().get_obs()

    def plot_object_2d(self):
        # TODO: Implement the logic to plot the blue object
        return super().plot_object_2d()

    def plot_object_3d(self):
        # TODO: Implement the logic to plot the blue object
        return super().plot_object_3d()

    def plot_launch_site_2d(self):
        # TODO: Implement the logic to plot the launch site
        return super().plot_launch_site_2d()

    def plot_launch_site_3d(self):
        # TODO: Implement the logic to plot the launch site
        return super().plot_launch_site_3d()
