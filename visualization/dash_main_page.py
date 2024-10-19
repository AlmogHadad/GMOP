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
from visualization.dash_utils import create_graph, create_leaflet_map
from red_object import RedObject
from blue_object import BlueObject

# Initialize the Dash app
app = Dash(external_stylesheets=dmc.styles.ALL)

simulation_manager = SimulationManager([], [])

app.layout = dmc.MantineProvider(
    html.Div([
        dmc.Grid([
            dmc.GridCol(children=[
                dmc.Stack(children=[
                    dmc.Button("Load Input", id="load-input-button"),
                    dmc.Button("Save Input", id="save-input-button"),
                    dmc.Button('Reset All', id='reset-all-button', n_clicks=0),
                    dmc.Button('Run Simulation', id='run-simulation-button', n_clicks=0),
                    dmc.Button('One Step', id='one-step-button', n_clicks=0),
                    dmc.Button('Pause / Resume Simulation', id='pause-simulation-button', n_clicks=0),
                    dmc.Button('Reset Simulation', id='reset-simulation-button', n_clicks=0),
                    dmc.Button('Add Blue Object', id='add-blue-button', n_clicks=0),
                    dmc.Button('Add Red Object', id='add-red-button', n_clicks=0)
                ],
                    gap='s',
                    align='left',
                )
            ],
                span=2
            ),

            dmc.GridCol(children=[
                dl.Map(id="leaflet-map", style={'height': '95vh', 'backgroundColor': 'white'},
                       center=[0, 0],
                       zoom=0,
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
                span=5
            ),
        ]),
        html.Div(id='trigger'),
        html.Div(id='red_object_alt_callback')
    ]),
)


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
    Output('leaflet-map', 'children', allow_duplicate=True),
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
def add_marker(n_clicks_blue, n_clicks_red):
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


@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('object-markers', 'children', allow_duplicate=True),
    Input({"type": "update-altitude", "index": ALL}, "n_clicks"),
    State({"type": "red_object_alt", "index": ALL}, "value"),
    prevent_initial_call=True
)
def update_red_object_altitude(input_alts, new_alt):
    # Check if there are no red objects, return early
    if len(simulation_manager.env.red_object_list) == 0:
        return no_update, no_update

    # check if any button was clicked (half of args are n_clicks)
    is_clicked = False
    for n_clicks in input_alts:
        if n_clicks:
            is_clicked = True
            break
    if not is_clicked:
        return no_update, no_update

    ctx = callback_context

    if not ctx.triggered:
        return no_update

    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    for i, red_object in enumerate(simulation_manager.env.red_object_list):
        # Check if this is the triggered input and if n_clicks is 0
        if ctx.triggered_id['index'] == red_object.id:
            print('inside')
            if input_alts[i] == 0:
                return no_update  # Do nothing if button hasn't been clicked

            new_altitude = new_alt[i]  # Get altitude value from input
            red_object.position[2] = new_altitude  # Update the altitude
            break

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
    return not n_clicks > 0

# Callback to pause / resume the simulation
@app.callback(Output('interval-component', 'disabled', allow_duplicate=True),
                Input('pause-simulation-button', 'n_clicks'),
                prevent_initial_call=True)
def pause_simulation(n_clicks):
    return not n_clicks % 2 == 0


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
