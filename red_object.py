import numpy as np
import plotly.graph_objs as go


class RedObject:
    _id_counter = 1  # Class-level variable to track the unique ID

    def __init__(self,
                 initial_position: np.ndarray = np.array([-50, -50, 50]),
                 velocity: np.ndarray = np.array([1, 0, 0])):
        self.id = RedObject._id_counter
        self.initial_position = initial_position.copy()
        self.position = initial_position.copy()
        self.velocity = velocity
        self.i_am_alive = True

        RedObject._id_counter += 1 # Increment the ID counter

    def step(self):
        if self.i_am_alive:
            self.position += self.velocity
        return self.position

    def reset(self):
        self.position = self.initial_position.copy()
        self.i_am_alive = True
        return self.position

    def get_obs(self):
        return self.position

    import plotly.graph_objs as go

    def plot_object(self):
        marker_symbol = 'circle' if self.i_am_alive else 'x'
        return go.Scatter3d(
            x=[self.position[0]],
            y=[self.position[1]],
            z=[self.position[2]],
            mode='markers',
            marker=dict(size=10, symbol=marker_symbol, color='red'),
            text=f'Object:\n id: {self.id} \n position: {self.position} \n velocity: {self.velocity}',
            showlegend=False
        )
