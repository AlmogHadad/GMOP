# global imports
from dash import Dash, html, dcc, _dash_renderer
_dash_renderer._set_react_version("18.2.0")
from dash.dependencies import Input, Output
import dash_mantine_components as dmc
import numpy as np

# local imports
from simulation_manager import SimulationManager
from dash_utils import create_graph


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
                    dmc.Button('Reset Simulation', id='reset-simulation-button', n_clicks=0)
                    ],
                    gap='s',
                    align='left',
                )
            ],
                span=2
            ),

            dmc.GridCol(children=[
                            dcc.Graph(id='live-update-graph', style={'height': '80vh'}),
                            dcc.Interval(
                                id='interval-component',
                                interval=100,  # Update every 100 milliseconds
                                n_intervals=0,
                                disabled=True
                            ),
                ],
                span=10
            )
        ]),

    ])
)


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
                Input('reset-simulation-button', 'n_clicks'),
                prevent_initial_call=True)
def reset_simulation(n_clicks):
    simulation_manager.reset()
    # create obs of the reset environment
    obs = np.concatenate((simulation_manager.env.interceptor_position, simulation_manager.env.target_position))
    return create_graph(obs)


# take one step
@app.callback(Output('live-update-graph', 'figure', allow_duplicate=True),
                Input('one-step-button', 'n_clicks'),
                prevent_initial_call=True)
def one_step(n_clicks):
    action = simulation_manager.take_action()
    obs, reward, done, _ = simulation_manager.step(action)

    return create_graph(obs)


@app.callback(Output('live-update-graph', 'figure', allow_duplicate=True),
              Input('interval-component', 'n_intervals'),
              prevent_initial_call=True)
def update_graph(n):
    action = simulation_manager.take_action()
    obs, reward, done, _ = simulation_manager.step(action)
    return create_graph(obs)


simulation_manager = SimulationManager()
if __name__ == '__main__':
    app.run_server(debug=True)