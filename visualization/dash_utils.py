import plotly.graph_objs as go


def create_graph(obs, current_time: int):
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
    # if Interceptor reaches the target
    if abs(obs[0] - obs[3]) <= 1 and abs(obs[1] - obs[4]) <= 1 and abs(obs[2] - obs[5]) <= 1:
        fig.add_annotation(
            x=0.5,
            y=0.5,
            showarrow=False,
            text="Target Destroyed! Time: " + str(current_time),
            xref="paper",
            yref="paper",
            font=dict(
                size=18,
            ),
        )
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

    # write current timr step
    fig.add_annotation(
        x=0.5,
        y=-0.1,
        showarrow=False,
        text=f"Time: {current_time}",
        xref="paper",
        yref="paper",
        font=dict(
            size=18,
        ),
    )

    return fig