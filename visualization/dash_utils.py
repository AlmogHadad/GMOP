import plotly.graph_objs as go
from simulation_manager import SimulationManager

def create_graph(simulation_manager: SimulationManager, view_3d=True):
    fig = go.Figure()

    # Add blue objects
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_object())

    # Add red objects
    for red_object in simulation_manager.env.red_object_list:
        fig.add_trace(red_object.plot_object())

    # Add launch sites
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_launch_site())

    # Set layout
    fig.update_layout(
        title='UAV Interceptor Visualization',
        uirevision='constant'  # Maintain user interactions (zoom, pan, etc.)
    )

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

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-100, 100], autorange=False),
            yaxis=dict(range=[-100, 100], autorange=False),
            zaxis=dict(range=[0, 100], autorange=False),
        ))

    # if 2d view is selected, set the camera to the top view
    if not view_3d:
        fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=0, y=0, z=2.5)))
    else:
        fig.update_layout(scene_camera=dict(up=dict(x=0, y=0, z=1), center=dict(x=0, y=0, z=0), eye=dict(x=1.25, y=1.25, z=1.25)))

    # set to orthographic view
    fig.update_layout(scene_camera=dict(projection=dict(type='orthographic')))

    return fig
