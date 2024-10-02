import plotly.graph_objs as go

def create_graph(obs):
    fig = go.Figure()

    # Interceptor
    fig.add_trace(go.Scatter3d(
        x=[obs[0]],
        y=[obs[1]],
        z=[obs[2]],
        mode='markers',
        marker=dict(size=10, color='blue'),
        name='Interceptor'
    ))

    # Target UAV
    fig.add_trace(go.Scatter3d(
        x=[obs[3]],
        y=[obs[4]],
        z=[obs[5]],
        mode='markers',
        marker=dict(size=10, color='red'),
        name='Target UAV'
    ))

    # Launch Point
    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        mode='markers',
        marker=dict(size=10, color='green'),
        name='Launch Point'
    ))

    # Set layout
    fig.update_layout(
        title='UAV Interceptor Visualization',
        uirevision='constant'  # Maintain user interactions (zoom, pan, etc.)
    )

    return fig