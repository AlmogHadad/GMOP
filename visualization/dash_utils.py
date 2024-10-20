import math
import numpy as np
import plotly.graph_objs as go
from simulation_manager import SimulationManager
from dash import html
from dash import dcc
import dash_mantine_components as dmc


def create_graph(simulation_manager: SimulationManager):
    # Create a subplot with 1 row and 2 columns
    fig = go.Figure()

    # Add blue objects to 3D map
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_object_3d())

    # Add red objects to 3D map
    for red_object in simulation_manager.env.red_object_list:
        fig.add_trace(red_object.plot_object_3d())

    # Add launch sites to 3D map
    for blue_object in simulation_manager.env.blue_object_list:
        fig.add_trace(blue_object.plot_launch_site_3d())

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
    fig.update_xaxes(range=[-100, 100])
    fig.update_yaxes(range=[-100, 100])

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


def velocity_to_degrees(vx, vy):
    # Calculate the angle in radians
    angle_rad = math.atan2(vy, vx)
    # Convert to degrees
    angle_deg = math.degrees(angle_rad)

    # Ensure the angle is between 0 and 360 degrees
    while angle_deg < 0:
        angle_deg += 360
    while angle_deg >= 360:
        angle_deg -= 360

    return angle_deg


def create_leaflet_map(simulation_manager: SimulationManager):
    import dash_leaflet as dl

    markers = []

    # Iterate over blue objects and create markers
    for blue_object in simulation_manager.env.blue_object_list:
        if blue_object.i_am_alive:
            position = blue_object.position[:2]  # Assuming 2D position (x, y)
            # plot blue object only if its not in the launch site
            if np.linalg.norm(blue_object.position - blue_object.launch_site_position) > 1:
                markers.append(
                    dl.Marker(
                        position=position.tolist(),
                        icon={
                            "iconUrl": f'assets/plane_blue/{int(velocity_to_degrees(blue_object.current_velocity[0], blue_object.current_velocity[1]))}.png',
                            "iconSize": [20, 20],
                            "iconAnchor": [20, 20],
                        },
                    )
                )

            markers.append(
                dl.Marker(
                    position=blue_object.launch_site_position[:2].tolist(),
                    icon={
                        "iconUrl": 'assets/launch_site.png',
                        "iconSize": [20, 20],
                        "iconAnchor": [20, 20],
                    },
                    children=[
                        dl.Popup(
                            children=[
                                html.Div([
                                    html.Label("Speed:"),
                                    dcc.Input(
                                        id={"type": "blue_object_speed", "index": blue_object.id},
                                        type='text',
                                        value=f'{blue_object.max_speed}'
                                    )
                                ])
                            ]
                        )
                    ]
                )
            )

    # Iterate over red objects and create markers
    for red_object in simulation_manager.env.red_object_list:
        if red_object.i_am_alive:
            position = red_object.position[:2]  # Assuming 2D position (x, y)
            markers.append(
                dl.Marker(
                    position=position.tolist(),
                    icon={
                        "iconUrl": f'assets/plane_red/{int(velocity_to_degrees(red_object.velocity[0], red_object.velocity[1]))}.png',
                        "iconSize": [20, 20],
                        "iconAnchor": [20, 20],
                    },
                    children=[
                        dl.Popup(
                            children=[
                                html.Div([
                                    html.Label("Altitude:"),
                                    dcc.Input(
                                        id={"type": "red_object_alt", "index": red_object.id},
                                        type='number',
                                        value=red_object.position[2],
                                        step=1
                                    ),
                                    html.Br(),
                                    html.Label("Velocity:"),
                                    dcc.Input(
                                        id={"type": "red_object_velocity", "index": red_object.id},
                                        type='text',
                                        value=f'{red_object.velocity[0]}, {red_object.velocity[1]}, {red_object.velocity[2]}'
                                    ),
                                ])
                            ]
                        )
                    ]
                )
            )

    # Combine markers and return them as map children
    return dl.LayerGroup(children=markers, id="blue-object-markers")
