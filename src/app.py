from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import datetime
import numpy as np
from dash_bootstrap_templates import load_figure_template

# loads the "darkly" template and sets it as the default
load_figure_template("darkly")

shots = ['Three', 'Set', 'Jumper', 'Free']  # shot types
data = {}
bad = []
sp = {}

arrays = [
    np.array(['Side', 'Shooting', 'Shooting', 'Non-shooting', 'Non-shooting']),
    np.array(['Shot Metric', 'Make', 'Miss', 'Make', 'Miss']),
]

titles = {
    'tables': ['Start of Shot (SS)', 'Set Point (SP)', 'Ball Release (BR)'],
    'angles': ['Right Wrist Angle', 'Right Elbow Angle', 'Right Shoulder Angle', 'Torso Angle',
               'Right Hip Angle', 'Right Knee Angle', 'Right Ankle Angle'],
    'velocities': ['Right Wrist Velocity', 'Right Elbow Velocity', 'Right Shoulder Velocity',
                   'Torso Velocity', 'Right Hip Velocity', 'Right Knee Velocity']
}


colored = [
    html.Th('Shot Metric'),
    html.Th('Make', style={'color': 'green'}),
    html.Th('Miss', style={'color': 'red'}),
    html.Th('Make', style={'color': 'green'}),
    html.Th('Miss', style={'color': 'red'})
    ]

for s in shots:
    try:
        data[s] = [pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/SS_side.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/SP_side.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/BR_side.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/SS_front.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/SP_front.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/BR_front.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/timing.csv?raw=true'),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/signals_make.csv?raw=true', index_col=0),
                   pd.read_csv('https://github.com/cdziuk/BasketballData/blob/main/' + s + '/signals_miss.csv?raw=true', index_col=0)]

        sp[s] = [(data[s][6]['Shooting Side'][5] / data[s][6]['Shooting Side'][6]) * 100,
                 (data[s][6]['Shooting Side.1'][5] / data[s][6]['Shooting Side.1'][6]) * 100]

        for x in range(7):
            data[s][x].columns = arrays

        data[s][7].columns = [format(x, '02d') for x in range(101)]
        data[s][8].columns = [format(x, '02d') for x in range(101)]

    except Exception:
        bad.append(s)

date = datetime.datetime.now().strftime("%m/%d/%Y")
time = datetime.datetime.now().strftime("%H:%M:%S")
athlete = "John Doe"

mcw_logo = 'https://github.com/cdziuk/BasketballData/blob/main/mcw_logo.png?raw=true'
ortho_logo = 'https://github.com/cdziuk/BasketballData/blob/main/ortho_logo.png?raw=true'
dunk = 'https://github.com/cdziuk/BasketballData/blob/main/dunk.png?raw=true'

[shots.remove(b) for b in bad]

# Initialize the app - incorporate a Dash Bootstrap theme
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.config.external_stylesheets = [dbc.themes.DARKLY, dbc.icons.FONT_AWESOME]

buttons = [{"label": s, "value": s} for s in shots]

header = dbc.Row([
        dbc.Col(html.Div(html.Img(src=mcw_logo, className="img-fluid"),
                         className='text-center'), width=2),
        dbc.Col([
            html.H1('BASKETBALL SHOOTING REPORT', className='text-center'),
            html.H2(athlete, className='text-center'),
            html.H3(date, className='text-center')
        ], width=6),
        dbc.Col(html.Div(html.Img(src=ortho_logo, className="img-fluid"),
                         className='text-center'), width=2)
    ], align="center", justify="evenly")


app.layout = dbc.Container([
    # header logos and metadata
    header,
    html.Hr(),
    # shot select buttons
    dbc.Button([
        html.I(className='fa-solid fa-basketball'),
        ' Shot Selection',
        html.Div([
            dbc.RadioItems(
                id="controls",
                className="btn-group",
                inputClassName="btn-check",
                labelClassName="btn btn-outline-light border-white",
                labelCheckedClassName="active btn-outline-dark",
                options=buttons,
                value="Set"
            )
        ])
    ], id='toggle', className='fixed-bottom col-1 mx-auto border-top border-right border-left border-white border-bottom-0', color='secondary', size='sm'),
    html.Br(),
    # event tables
    dbc.Spinner(
            [
                html.Div(id="start_tables"),
                html.Br()
            ],
            delay_show=100,
        ),
    dbc.Spinner(
            [
                html.Div(id="set_tables"),
                html.Br()
            ],
            delay_show=100,
        ),
    dbc.Spinner(
            [
                html.Div(id="release_tables")
            ],
            delay_show=100,
        ),
    html.Hr(),
    dbc.Tabs(
            [
                dbc.Tab(label="Kinematics", tab_id="kinematics"),
                dbc.Tab(label="Timing", tab_id="timing"),
            ],
            id="tabs",
            active_tab="kinematics",
        ),
    dbc.Spinner(
            [
                dcc.Store(id="store"),
                html.Div(id="signal_graphs"),
                html.Div(id="signals"),
            ],
            delay_show=100,
        ),
    html.Hr(),
    dbc.Spinner(
        [
            html.Div(id="timing_table"),
            html.Br()
        ],
        delay_show=100,
    )
], fluid=True)


@app.callback(
    Output('controls', 'style'),
    [Input('toggle', 'n_clicks')],
    )
def button_toggle(n_clicks):
    if n_clicks is None:
        return {'display': 'none'}
    elif n_clicks % 2 == 1:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output("signal_graphs", "children"), Output("signals", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)
def render_tab_content(active_tab, dat):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab and dat is not None:
        if active_tab == "timing":
            return dat['timing'], dat['velocity']
        elif active_tab == "kinematics":
            return dat['angle'], dat['kinematic']
    return "No tab selected"


# Add controls to build the interaction
@callback(
    Output(component_id='start_tables', component_property='children'),
    Output(component_id='set_tables', component_property='children'),
    Output(component_id='release_tables', component_property='children'),
    Output(component_id='timing_table', component_property='children'),
    Input(component_id='controls', component_property='value')
)
def update_tables(chosen):
    tabs = []
    for i in range(7):
        t = dbc.Table.from_dataframe(data[chosen][i],
                                                striped=True,
                                                bordered=True,
                                                hover=True,
                                                color="dark")
        t.children[0].children[1].children = colored
        tabs.append(t)


    event_tables = []
    for i in range(3):
        tab = dbc.Card(
            dbc.CardBody([
                html.H3(titles['tables'][i], className='text-center'),
                dbc.Row([
                    dbc.Col([
                        html.H4('Front View', className='text-center'),
                        tabs[i]
                    ]),
                    dbc.Col([
                        html.H4('Side View', className='text-center'),
                        tabs[i+3]
                    ])
                ])
            ]),
            color="dark",
            outline=True,
            inverse=True
        )
        event_tables.append(tab)

    timing_table = dbc.Card(
        dbc.CardBody([
                    html.H3('Timing Table', className='text-center'),
                    dbc.Row([
                        tabs[6]
                    ])
        ]),
        color="dark",
        outline=True,
        inverse=True
    )
    return event_tables[0], event_tables[1], event_tables[2], timing_table


@callback(
    Output(component_id='store', component_property='data'),
    Input(component_id='controls', component_property='value')
)
def update_signals(chosen):
    timing_fig = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=px.line(data[chosen][7].iloc[7:13, 0:102].T, title=chosen + ' Timing Signals',
                                       labels={'index': 'Percent Shot %', 'value': 'Velocity m/s'},
                                       )
                        .add_vline(
                            x=sp[chosen][0],
                            line_width=3,
                            line_dash="dash",
                            line_color="green")
                        .add_vline(
                            x=sp[chosen][1],
                            line_width=3,
                            line_dash="dash",
                            line_color="red")
                        .update_layout(title_x=0.5,
                                       legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=1.02,
                                        xanchor="right",
                                        x=1
                                        ),
                                       xaxis=dict(
                                           dtick=5
                                       ),
                                       legend_title_text='Signal:')
                    )
                ])
            ])
        ]),
        color="dark",
        outline=True,
        inverse=True
    )

    fig = dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        figure=px.line(data[chosen][7].iloc[0:7, 0:102].T, title=chosen + ' Kinematic Signals',
                                       labels={'index': 'Percent Shot %', 'value': 'Degrees \N{DEGREE SIGN}'}
                                       )
                        .add_vline(
                            x=sp[chosen][0],
                            line_width=3,
                            line_dash="dash",
                            line_color="green")
                        .add_vline(
                            x=sp[chosen][1],
                            line_width=3,
                            line_dash="dash",
                            line_color="red")
                        .update_layout(title_x=0.5,
                                       legend=dict(
                                           orientation="h",
                                           yanchor="bottom",
                                           y=1.02,
                                           xanchor="right",
                                           x=1
                                       ),
                                       xaxis=dict(
                                           dtick=5
                                       ),
                                       legend_title_text='Signal:')
                    )
                ])
            ])
        ]),
        color="dark",
        outline=True,
        inverse=True
    )

    kinematic_graphs = []
    for i in range(7):
        tab = dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4([titles['angles'][i], html.Span(' Make', style={'color': 'green'})], className='text-center'),
                        dcc.Graph(
                            figure=px.line(data[chosen][7].iloc[i, 0:102].T,
                                           labels={'index': 'Percent Shot %', 'value': 'Degrees \N{DEGREE SIGN}'})
                            .add_vline(
                                x=sp[chosen][0],
                                line_width=2,
                                line_dash="dash",
                                line_color="green")
                            .update_traces(showlegend=False)
                            .update_layout(title_x=0.5,
                                           xaxis=dict(
                                               dtick=5),
                                           )
                        )
                    ]),
                    dbc.Col([
                        html.H4([titles['angles'][i], html.Span(' Miss', style={'color': 'red'})],
                                className='text-center'),
                        dcc.Graph(
                            figure=px.line(data[chosen][8].iloc[i, 0:102].T,
                                           labels={'index': 'Percent Shot %', 'value': 'Degrees \N{DEGREE SIGN}'})
                            .add_vline(
                                x=sp[chosen][1],
                                line_width=2,
                                line_dash="dash",
                                line_color="red")
                            .update_traces(showlegend=False)
                            .update_layout(title_x=0.5,
                                           xaxis=dict(
                                               dtick=5),
                                           )
                        )
                    ])
                ])
            ]),
            color='dark',
            outline=True,
            inverse=True
        )
        kinematic_graphs.append(tab)

    timing_graphs = []
    for i in range(6, 12):
        tab = dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H4([titles['velocities'][i-6], html.Span(' Make', style={'color': 'green'})],
                                className='text-center'),
                        dcc.Graph(
                            figure=px.line(data[chosen][7].iloc[i, 0:102].T,
                                           labels={'index': 'Percent Shot %', 'value': 'Velocity m/s'}
                                           )
                            .add_vline(
                                x=sp[chosen][0],
                                line_width=2,
                                line_dash="dash",
                                line_color="green")
                            .update_traces(showlegend=False)
                            .update_layout(title_x=0.5,
                                           xaxis=dict(
                                               dtick=5),
                                           )
                        )
                    ]),
                    dbc.Col([
                        html.H4([titles['velocities'][i-6], html.Span(' Miss', style={'color': 'red'})],
                                className='text-center'),
                        dcc.Graph(
                            figure=px.line(data[chosen][8].iloc[i, 0:102].T,
                                           labels={'index': 'Percent Shot %', 'value': 'Velocity m/s'},
                                           )
                            .add_vline(
                                x=sp[chosen][1],
                                line_width=2,
                                line_dash="dash",
                                line_color="red")
                            .update_traces(showlegend=False)
                            .update_layout(title_x=0.5,
                                           xaxis=dict(
                                               dtick=5),
                                           )
                        )
                    ])
                ])
            ]),
            color='dark',
            outline=True,
            inverse=True
        )
        timing_graphs.append(tab)

    return {"angle": fig, "timing": timing_fig, "kinematic": kinematic_graphs, "velocity": timing_graphs}


if __name__ == "__main__":
    app.run(debug=True)
