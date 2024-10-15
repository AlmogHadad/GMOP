# global imports
from dash import Dash, html, dcc, _dash_renderer, State, no_update
_dash_renderer._set_react_version("18.2.0")
from dash.dependencies import Input, Output
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

app.layout = dmc.MantineProvider(
    html.Div([
        dmc.Grid([
            dmc.GridCol(children=[
                dmc.Stack(children=[
                    dmc.Button('Run Simulation', id='run-simulation-button', n_clicks=0),
                    dmc.Button('One Step', id='one-step-button', n_clicks=0),
                    dmc.Button('Pause / Resume Simulation', id='pause-simulation-button', n_clicks=0),
                    dmc.Button('Reset Simulation', id='reset-simulation-button', n_clicks=0),
                    dmc.Text('Add Blue Object'),
                    dmc.TextInput(id='blue-position', placeholder='Position (x, y)'),
                    dmc.TextInput(id='blue-max-speed', placeholder='Max Speed (default: 3)'),
                    dmc.Button('Add Blue Object', id='add-blue-button', n_clicks=0),
                    dmc.Text('Add Red Object'),
                    dmc.TextInput(id='red-position', placeholder='Position (x, y, z)'),
                    dmc.TextInput(id='red-velocity', placeholder='Velocity (x, y, z)'),
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
                           dl.TileLayer(),  # Default OpenStreetMap layer
                           dl.LayerGroup(id="red-object-markers"),  # Red object markers
                           dl.LayerGroup(id="blue-object-markers"),  # Blue object markers
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
        ])
    ])
)


@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('red-position', 'value'),
    Output('red-velocity', 'value'),
    Output('leaflet-map', 'children', allow_duplicate=True),  # Add Leaflet output
    Input('add-red-button', 'n_clicks'),
    State('red-position', 'value'),
    State('red-velocity', 'value'),
    prevent_initial_call=True
)
def add_red_object(n_clicks, position, velocity):

    if n_clicks > 0:
        if position == '' or velocity == '':
            return no_update, no_update, no_update

        # Parse input strings for position and velocity
        position = np.array(list(map(float, position.split(','))))
        velocity = np.array(list(map(float, velocity.split(','))))
        # Create a new RedObject and add to simulation
        new_red = RedObject(position, velocity)
        simulation_manager.env.red_object_list.append(new_red)


        return create_graph(simulation_manager), '', '', create_leaflet_map(simulation_manager)

    return no_update, no_update, no_update, no_update

@app.callback(
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('blue-position', 'value'),
    Output('blue-max-speed', 'value'),
    Output('leaflet-map', 'children', allow_duplicate=True),  # Add Leaflet output
    Input('add-blue-button', 'n_clicks'),
    State('blue-position', 'value'),
    State('blue-max-speed', 'value'),
    prevent_initial_call=True
)
def add_blue_object(n_clicks, position, max_speed):

    if n_clicks > 0:
        # Parse input strings for position and max speed
        if position == '':
            return no_update, no_update, no_update

        position = np.array(list(map(float, position.split(','))))

        if max_speed == '':
            max_speed = 3
        max_speed = float(max_speed)

        # Create a new BlueObject and add to simulation
        new_blue = BlueObject(position, max_speed)
        simulation_manager.env.blue_object_list.append(new_blue)

        return create_graph(simulation_manager), '', '', create_leaflet_map(simulation_manager)

    return no_update, no_update, no_update, no_update

# Callback for the initial graph
@app.callback(Output('live-update-graph', 'figure'),
              Output('leaflet-map', 'children'),
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

@app.callback(Output('live-update-graph', 'figure', allow_duplicate=True),
                Output('leaflet-map', 'children', allow_duplicate=True),
                Input('reset-simulation-button', 'n_clicks'),
                prevent_initial_call=True)
def reset_simulation(_):

    simulation_manager.reset()
    # create obs of the reset environment
    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)

# take one step
@app.callback(Output('live-update-graph', 'figure', allow_duplicate=True),
              Output('leaflet-map', 'children', allow_duplicate=True),
                Input('one-step-button', 'n_clicks'),
                prevent_initial_call=True)
def one_step(_):

    action = simulation_manager.env.take_action()
    obs, reward, done, _ = simulation_manager.step(action)

    return create_graph(simulation_manager), create_leaflet_map(simulation_manager)

@app.callback(
    Output('leaflet-map', 'children', allow_duplicate=True),
    Output('live-update-graph', 'figure', allow_duplicate=True),
    Output('interval-component', 'disabled'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def update_graph(_):

    action = simulation_manager.env.take_action()
    obs, reward, done, _ = simulation_manager.step(action)

    return create_leaflet_map(simulation_manager), create_graph(simulation_manager), done

red_object1 = RedObject()
red_object2 = RedObject(np.array([-50, -30, 50]), np.array([0, 1, 0]))
blue_object = BlueObject()
simulation_manager = SimulationManager([red_object1, red_object2], [blue_object])

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
