# global imports
from dash import Dash, html, dcc, _dash_renderer, no_update, callback_context, ALL
_dash_renderer._set_react_version("18.2.0")
from dash import callback, Input, Output, State
import json
import easygui
import dash_mantine_components as dmc
import numpy as np
import dash_leaflet as dl

# local imports
from simulation_manager import SimulationManager
from visualization.dash_utils import create_graph, create_leaflet_map, calc_velocity_from_angle, calc_velocity_from_speed
from red_object import RedObject
from blue_object import BlueObject

# Initialize the Dash app
app = Dash(external_stylesheets=dmc.styles.ALL)

simulation_manager = SimulationManager([], [])

# Reference point (center of the map in Leaflet)
center_lat, center_lng = 32.0, 35.0

# Convert bounds from meters to degrees
latitude_bound = [-100 / 111000, 100 / 111000]  # ~[-0.0009, 0.0009]
longitude_bound = [-100 / 93000, 100 / 93000]  # ~[-0.00108, 0.00108]

# Calculate southwest and northeast corners of the bounds
southwest_bound = [center_lat + latitude_bound[0], center_lng + longitude_bound[0]]
northeast_bound = [center_lat + latitude_bound[1], center_lng + longitude_bound[1]]

app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    children=[
        html.Div([
            dmc.Grid([
                dmc.GridCol(children=[
                    dmc.Stack(children=[
                        dmc.Group([
                            dmc.Text('Inputs:\n'),
                            dmc.Button("Load Input", id="load-input-button", variant='overlay', fullWidth=True),
                            dmc.Button("Save Input", id="save-input-button", variant='overlay', fullWidth=True),
                        ]),
                        dmc.Group([
                            dmc.Text('Simulation Control:\n'),
                            dmc.Button('Run Simulation', id='run-simulation-button', n_clicks=0, fullWidth=True, size='l'),
                            dmc.Button('One Step', id='one-step-button', n_clicks=0, fullWidth=True),
                            dmc.Button('Pause / Resume Simulation', id='pause-simulation-button', n_clicks=0, color='red', fullWidth=True),
                            dmc.Button('Reset Simulation', id='reset-simulation-button', n_clicks=0, color='red', fullWidth=True),
                        ]),
                        dmc.Group([
                            dmc.Text('Objects:\n'),
                            dmc.Button('Add Blue Object', id='add-blue-button', n_clicks=0, color='green', fullWidth=True),
                            dmc.Button('Add Red Object', id='add-red-button', n_clicks=0, color='red', fullWidth=True),
                            dmc.Button('Clear Objects', id='clear-objects-button', n_clicks=0, fullWidth=True),
                        ]),
                    ],
                        gap='s',
                        align='center',
                    )
                ],
                    style={'padding-top': '30px'},
                    span=2
                ),

                dmc.GridCol(children=[
                    dl.Map(id="leaflet-map", style={'height': '95vh', 'backgroundColor': 'white'},
                           center=[center_lat, center_lng],
                           bounds=[southwest_bound, northeast_bound],
                           zoom=2,
                           crs="Simple",
                           children=[
                               dl.LayerGroup(id="object-markers"),

                               dl.FeatureGroup(
                                   [dl.EditControl(id="edit_control", position="topleft",
                                                   draw=dict(
                                                       marker=True,
                                                       circle=False,
                                                       circlemarker=False,
                                                       polygon=False,
                                                       polyline=False,
                                                       rectangle=False
                                                   )
                                                   )]),
                           ]),
                ],
                    style={'padding-top': '30px'},
                    span=5
                ),

                dmc.GridCol(children=[
                    dcc.Graph(id='live-update-graph', style={'height': '95vh'}),
                    dcc.Interval(
                        id='interval-component',
                        interval=500,  # Update every 500 milliseconds
                        n_intervals=0,
                        disabled=True
                    ),
                ],
                    style={'padding-top': '30px'},
                    span=5
                ),
            ]),
            html.Div(id='trigger'),
            html.Div(id='red_object_alt_callback'),
        ]),
    ]
)


# Callback to clear all objects
@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Input('clear-objects-button', 'n_clicks'),
    prevent_initial_call=True
)
def clear_objects(n_clicks):
    if n_clicks is None or n_clicks == 0:
        return no_update, no_update

    simulation_manager.env.red_object_list = []
    simulation_manager.env.blue_object_list = []
    simulation_manager.time = 0

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


@callback(
    Output('trigger', 'children', allow_duplicate=True),
    Input('save-input-button', 'n_clicks'),
    prevent_initial_call=True
)
def save_scenario(save_clicks):
    if save_clicks is None or save_clicks == 0:
        return no_update

    # Save the current state of red and blue objects to a file
    save_data = {
        "blue_objects": [blue_object.to_dict() for blue_object in simulation_manager.env.blue_object_list],
        "red_objects": [red_object.to_dict() for red_object in simulation_manager.env.red_object_list]
    }
    filepath = easygui.filesavebox('save scenario file', default='./', filetypes=['*.json'])
    filepath = filepath.split('.')[0] + '.json' if not filepath.split('.')[0].endswith('.json') else filepath.split('.')[0]
    with open(filepath, "w") as f:
        json.dump(save_data, f, indent=4)

    return no_update


@callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Input('load-input-button', 'n_clicks'),
    prevent_initial_call=True
)
def load_scenario(load_clicks):
    if load_clicks is None or load_clicks == 0:
        return no_update

    # Load the saved object data from the file
    filepath = easygui.fileopenbox('select scenario file', default='./', filetypes=['*.json'])
    with open(filepath, "r") as file:
        load_data = json.load(file)  # Load the JSON data

    # Update simulation manager's environment with loaded data
    simulation_manager.env.blue_object_list = [BlueObject(np.array(data['position'], dtype=np.float64), float(data['max_speed'])) for data in
                                               load_data['blue_objects']]
    simulation_manager.env.red_object_list = [RedObject(np.array(data['position'], dtype=np.float64), np.array(data['velocity'], dtype=np.float64)) for data in
                                              load_data['red_objects']]

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


# Callback to add blue object
edit_mode = None
@app.callback(
    Output("edit_control", "drawToolbar", allow_duplicate=True),
    [Input('add-blue-button', 'n_clicks'),
     Input('add-red-button', 'n_clicks')],
    prevent_initial_call=True
)
def add_marker(_, __):
    global edit_mode
    ctx = callback_context

    if not ctx.triggered:
        return no_update

    # Determine which button was clicked
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id == 'add-blue-button':
        edit_mode = 'blue'
    elif triggered_id == 'add-red-button':
        edit_mode = 'red'

    return dict(mode="marker")


@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Output("edit_control", "editToolbar"),
    Input('edit_control', 'geojson'),
    prevent_initial_call=True
)
def add_objects(geojson):
    global edit_mode
    if geojson:

        features = geojson['features']
        if features:
            # Get the coordinates of the last added marker
            coordinates = features[-1]['geometry']['coordinates']
            if edit_mode == 'blue':
                position = np.array([coordinates[1], coordinates[0], 0])  # Note: Leaflet uses [lng, lat]
                max_speed = float(3)
                new_blue = BlueObject(position, max_speed)
                simulation_manager.env.blue_object_list.append(new_blue)

            elif edit_mode == 'red':
                position = np.array([coordinates[1], coordinates[0], 0])
                velocity = np.array([1, 0, 0])
                new_red = RedObject(position, velocity)
                simulation_manager.env.red_object_list.append(new_red)

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager), dict(mode="remove", action="clear all")


def is_valid_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Input({"type": "red_object_alt", "index": ALL}, "value"),
    Input({"type": "red_object_velocity", "index": ALL}, "value"),
    Input({"type": "red_object_angle", "index": ALL}, "value"),
    Input({"type": "red_object_speed", "index": ALL}, "value"),
    Input({"type": "red_object_delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_red_object(new_alt, new_vel, new_angle, new_speed, new_delete):
    # Check if there are no red objects, return early
    if len(simulation_manager.env.red_object_list) == 0:
        return no_update, no_update

    ctx = callback_context

    if not ctx.triggered:
        return no_update
    alive_red_objects = []
    for red_object in simulation_manager.env.red_object_list:
        if red_object.i_am_alive:
            alive_red_objects.append(red_object)

    for i, red_object in enumerate(alive_red_objects):
        # Check if this is the triggered input and if n_clicks is 0
        if ctx.triggered_id['index'] == red_object.id:
            if new_vel[i] is None or new_alt[i] is None:
                return no_update  # Do nothing if button hasn't been clicked

            red_object.position[2] = new_alt[i]  # Update the altitude
            if ctx.triggered_id['type'] == 'red_object_velocity':
                splitted_velocity = new_vel[i].split(',')
                # check the all the 3 values is valid numbers

                if new_vel[i] is None or len(splitted_velocity) != 3 or not all(is_valid_number(v) for v in splitted_velocity):
                    return no_update

                red_object.velocity = np.array(new_vel[i].split(','), dtype=np.float64)
            elif ctx.triggered_id['type'] == 'red_object_angle':
                if new_angle[i] is None:
                    return no_update
                red_object.velocity = calc_velocity_from_angle(red_object.velocity, new_angle[i])

            elif ctx.triggered_id['type'] == 'red_object_speed':
                if new_speed[i] is None:
                    return no_update
                red_object.velocity = calc_velocity_from_speed(red_object.velocity, new_speed[i])

            elif ctx.triggered_id['type'] == 'red_object_delete':
                # remove the red object
                simulation_manager.env.red_object_list.pop(i)
            break

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


# Callback to update the max speed of the blue object
@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Input({"type": "blue_object_speed", "index": ALL}, "value"),
    Input({"type": "blue_object_delete", "index": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def update_blue_object(new_speed, new_delete):
    # Check if there are no blue objects, return early
    if len(simulation_manager.env.blue_object_list) == 0:
        return no_update, no_update

    ctx = callback_context

    if not ctx.triggered:
        return no_update

    for i, blue_object in enumerate(simulation_manager.env.blue_object_list):
        # Check if this is the triggered input and if n_clicks is 0
        if ctx.triggered_id['index'] == blue_object.id:
            if ctx.triggered_id['type'] == 'blue_object_speed':
                if new_speed[i] == 0 or new_speed[i] is None:
                    return no_update

                try:
                    blue_object.max_speed = float(new_speed[i])  # Update the max speed
                except ValueError:
                    return no_update
                break

            elif ctx.triggered_id['type'] == 'blue_object_delete':
                simulation_manager.env.blue_object_list.pop(i)

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


# Callback for the initial graph
@app.callback(Output('live-update-graph', 'figure'),
              Output('object-markers', 'children'),
              Input('interval-component', 'n_intervals'),
              )
def initial_graph(_):
    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


# Callback to run the simulation
@app.callback(Output('interval-component', 'disabled', allow_duplicate=True),
              Input('run-simulation-button', 'n_clicks'),
              prevent_initial_call=True)
def run_simulation(n_clicks):
    if len(simulation_manager.env.red_object_list) < 1 or len(simulation_manager.env.blue_object_list) < 1:
        return no_update

    return not n_clicks > 0

# Callback to pause / resume the simulation
@app.callback(Output('interval-component', 'disabled', allow_duplicate=True),

                Output('pause-simulation-button', 'color'),
                Input('pause-simulation-button', 'n_clicks'),
                prevent_initial_call=True)
def pause_simulation(n_clicks):
    if len(simulation_manager.env.red_object_list) < 1 or len(simulation_manager.env.blue_object_list) < 1:
        return no_update

    return not n_clicks % 2 == 0, 'red' if n_clicks % 2 == 0 else 'green'


# Callback to reset the simulation
@app.callback(Output('live-update-graph', 'figure', allow_duplicate=True),
              Output('object-markers', 'children', allow_duplicate=True),
              Input('reset-simulation-button', 'n_clicks'),
              prevent_initial_call=True)
def reset_simulation(_):
    simulation_manager.reset()
    # create obs of the reset environment
    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


# take one step
@app.callback(Output('live-update-graph', 'figure', allow_duplicate=True),
              Output('object-markers', 'children', allow_duplicate=True),
                Input('one-step-button', 'n_clicks'),
                prevent_initial_call=True)
def one_step(_):
    if len(simulation_manager.env.red_object_list) < 1 or len(simulation_manager.env.blue_object_list) < 1:
        return no_update

    action = simulation_manager.env.take_action()
    obs, reward, done, _ = simulation_manager.step(action)

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)


@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Output('interval-component', 'disabled'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def update_graph(_):

    action = simulation_manager.env.take_action()
    obs, reward, done, _ = simulation_manager.step(action)

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager), done


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
