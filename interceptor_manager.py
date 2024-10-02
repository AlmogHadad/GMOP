import numpy as np


class InterceptorManager:
    def __init__(self):
        self.launch_site_position = np.array([0, 0, 0], dtype=np.float64)
        self.number_of_interceptors = 1

    def