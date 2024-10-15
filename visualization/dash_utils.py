import plotly.graph_objs as go
from plotly.subplots import make_subplots
from simulation_manager import SimulationManager

def create_graph(simulation_manager: SimulationManager, view_3d: bool = True):
    # Create a subplot with 1 row and 2 columns
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type': 'scatter3d'}, {'type': 'scatter'}]],
        subplot_titles=("3D Map", "2D Map")
    )

    # Add blue objects to 3D map
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_object_3d(), row=1, col=1)

    # Add red objects to 3D map
    for red_object in simulation_manager.env.red_object_list:
        fig.add_trace(red_object.plot_object_3d(), row=1, col=1)

    # Add launch sites to 3D map
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_launch_site_3d(), row=1, col=1)

    # Add blue objects to 2D map
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_object_2d(), row=1, col=2)

    # Add red objects to 3D map
    for red_object in simulation_manager.env.red_object_list:
        fig.add_trace(red_object.plot_object_2d())

    # Add launch sites to 2D map
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_launch_site_2d(), row=1, col=2)

    # Set layout for 3D map
    fig.update_layout(
        title='UAV Interceptor Visualization',
        uirevision='constant',  # Maintain user interactions (zoom, pan, etc.)
        scene=dict(
            xaxis=dict(range=[-100, 100], autorange=False),
            yaxis=dict(range=[-100, 100], autorange=False),
            zaxis=dict(range=[0, 100], autorange=False),
        ),
        scene_camera=dict(projection=dict(type='orthographic'))
    )

    # Set layout for 2D map
    fig.update_xaxes(range=[-100, 100], row=1, col=2)
    fig.update_yaxes(range=[-100, 100], row=1, col=2)

    # Display time step
    fig.add_annotation(
        x=0.5,
        y=-0.1,
        showarrow=False,
        text=f"Time: {simulation_manager.time}",
        xref="paper",
        yref="paper",
        font=dict(size=18),
    )

    return fig
