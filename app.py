import flask
from flask_caching import Cache

import plotly.graph_objects as go
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import State, Input, Output
import dash_daq as daq

import utils.dash_reusable_components as drc

import numpy as np
import pandas as pd
import json
import os
import random

#--------------------------------------------------------------------
#                        Load Configs
#--------------------------------------------------------------------

with open('./config.json') as config_file:
    config = json.load(config_file)

mapbox_access_token = config['mapbox-token']
mapbox_style = config['mapbox_style']
px.set_mapbox_access_token(mapbox_access_token)

#--------------------------------------------------------------------
#                       Initialise App
#--------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    meta_tags = [
        {
            "name": "description",
            "content": "CoVID-19 India Prediction"
        },
        {
            "name": "viewport",
            "content": "width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"
        }
    ]
)

app.title = "CoVID-19 Vaccine Efficacy"

server = app.server

app.config["suppress_callback_exceptions"] = True

#--------------------------------------------------------------------
#                           Load files
#--------------------------------------------------------------------

state_map = {
    "IN": {"state": "India", "lat": 12.698214530944824, "long": 92.85771179199219, "zoom": 3},
    "AN": {"state": "Andaman and Nicobar Islands", "lat": 12.698214530944824, "long": 92.85771179199219, "zoom": 5},
    "AP": {"state": "Andhra Pradesh", "lat": 15.9240905, "long": 80.1863809, "zoom": 5},
    "AR": {"state": "Arunachal Pradesh", "lat": 28.0937702, "long": 94.5921326, "zoom": 5.5},
    "AS": {"state": "Assam", "lat": 26.4073841, "long": 93.2551303, "zoom": 5},
    "BH": {"state": "Bihar", "lat": 25.6440845, "long": 85.906508, "zoom": 5.3},
    "CH": {"state": "Chandigarh", "lat": 30.7334421, "long": 76.7797143, "zoom": 10},
    "CG": {"state": "Chhattisgarh", "lat": 21.295132, "long": 81.828232, "zoom": 5.1},
    "DD": {"state": "Dadra and Nagar Haveli and Daman and Diu", "lat": 20.7179857, "long": 70.9323992, "zoom": 5.5},
    "DL": {"state": "Delhi", "lat": 28.6517178, "long": 77.2219388, "zoom": 8},
    "GA": {"state": "Goa", "lat": 15.3004543, "long": 74.0855134, "zoom": 7},
    "GJ": {"state": "Gujarat", "lat": 22.309425, "long": 72.136230, "zoom": 5},
    "HR": {"state": "Haryana", "lat": 29.238478, "long": 76.431885, "zoom": 6},
    "HP": {"state": "Himachal Pradesh", "lat": 32.084206, "long": 77.571167, "zoom": 6},
    "JK": {"state": "Jammu and Kashmir", "lat": 33.5574473, "long": 75.06152, "zoom": 6.2},
    "JH": {"state": "Jharkhand", "lat": 23.4559809, "long": 85.2557301, "zoom": 5.5},
    "KA": {"state": "Karnataka", "lat": 15.317277, "long": 75.713890, "zoom": 5},
    "KL": {"state": "Kerala", "lat": 10.850516, "long": 76.271080, "zoom": 5.3},
    "LA": {"state": "Ladakh", "lat": 34.9456407, "long": 76.1568576, "zoom": 5},
    "MP": {"state": "Madhya Pradesh", "lat": 23.473324, "long": 78.347998, "zoom": 4.8},
    "MH": {"state": "Maharashtra", "lat": 19.601194, "long": 77.152979, "zoom": 4.8},
    "MN": {"state": "Manipur", "lat": 24.7208818, "long": 93.9229386, "zoom": 5},
    "ML": {"state": "Meghalaya", "lat": 25.5379432, "long": 91.2999102, "zoom": 6},
    "MZ": {"state": "Mizoram", "lat": 23.2146169, "long": 92.8687612, "zoom": 6.5},
    "NL": {"state": "Nagaland", "lat": 26.1630556, "long": 94.5884911, "zoom": 5},
    "OD": {"state": "Odisha", "lat": 20.940920, "long": 84.803467, "zoom": 5},
    "PY": {"state": "Puducherry", "lat": 11.941552, "long": 79.808289, "zoom": 8},
    "PB": {"state": "Punjab", "lat": 31.147129, "long": 75.341217, "zoom": 6.2},
    "RJ": {"state": "Rajasthan", "lat": 27.891277, "long": 74.432617, "zoom": 4.5},
    "SK": {"state": "Sikkim", "lat": 27.606001, "long": 88.473167, "zoom": 5},
    "TN": {"state": "Tamil Nadu", "lat": 11.059821, "long": 78.387451, "zoom": 5},
    "TS": {"state": "Telangana", "lat": 17.123184, "long": 79.208824, "zoom": 5},
    "TR": {"state": "Tripura", "lat": 23.745127, "long": 23.745127, "zoom": 5},
    "UP": {"state": "Uttar Pradesh", "lat": 26.244156, "long": 92.537842, "zoom": 5},
    "UK": {"state": "Uttarakhand", "lat": 30.379910, "long": 78.877386, "zoom": 6},
    "WB": {"state": "West Bengal", "lat": 23.578624, "long": 87.747803, "zoom": 5},
}

state_list = list(state_map.keys())

with open('./assets/states-and-districts.json') as dist_json:
    state_districts_data = json.load(dist_json)


# Load national and statewise data
india_data = pd.read_csv('./data/state_data/prediction_IN.csv')

data_dict = {}
for state in state_list:
    p = os.getcwd().split(os.path.sep)
    csv_path = "./data/state_data/prediction_{}.csv".format(state)
    state_data = pd.read_csv(csv_path)
    data_dict[state] = state_data

# Load GeoJsons

# Change this to state and change the entire logic later
india_gj = "./maps/india_districts.geojson"

gj_dict = {}
for state in state_list:
    p = os.getcwd().split(os.path.sep)
    geojson_path = "./maps/{}.geojson".format(state)
    gj_dict[state] = geojson_path

#--------------------------------------------------------------------
#                         Layout Helpers
#--------------------------------------------------------------------


#----------------------
#        Tab-1
#----------------------

def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className="four columns"),
            html.Label(value, className="four columns"),
            html.Div(col3, className="four columns"),
        ],
        className="row",
    )


#---------------------- 
#        Tab-2
#----------------------

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("CoVID-19 Vaccine Efficacy"),
                    html.H6("Vaccine efficacy and herd immunity predictor"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.Button(
                        id="learn-more-button", children="LEARN MORE", n_clicks=0
                    ),
                    html.Img(id="logo", src=app.get_asset_url("dash-logo-new.png")),
                ],
            ),
        ],
    )

def build_modal():
    return html.Div(
        id="markdown",
        className="modal",
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className="close-container",
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton",
                        ),
                    ),
                    html.Div(
                        className="markdown-text",
                        children=dcc.Markdown(
                            children=(
                    """
                        ###### What is this mock app about?

                        This is a dashboard for monitoring the CoVID-19 vaccine efficacy in India.

                        ###### What does this app show

                        Shows nothing as of now.

                    """
                            )
                        ),
                    ),
                ],
            )
        ),
    )

def build_left_panel():
    return html.Div(
        id="quick-stats",
        className="column",
        children=[
            generate_section_banner("Put a heading here"),
            # Choose State
            drc.NamedDropdown(
                name="Select State",
                id="dropdown-select-state",
                options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                clearable=False,
                searchable=True,
                value="AP",
            ),

            drc.NamedDropdown(
                name="Select State",
                id="dropdown-select-district",
                # options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                options= [ {"label" : i, "value" : i} for i in state_districts_data['states'][0]['districts'] ],
                clearable=False,
                searchable=True,
                value="Anantapur",
            ),

            dcc.RadioItems(
                options=[
                    {'label': 'New Cases', 'value': 'NC'},
                    {'label': 'Recovered', 'value': 'RC'},
                    {'label': 'Vaccinated', 'value': 'VC'}
                ],
                value='NC'
            )
        ]
    )

def generate_metric_row(id, style, col1, col2):
    if style is None:
        style = {"height": "8rem", "width": "100%"}

    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one columns",
                style={"marginRight": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"height": "100%"},
                className="four columns",
                children=col2["children"],
            )
        ]
    )

suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"

params = ['Last one Month', 'Next 10 days']

def generate_metric_row_helper(index, state=None, district=None, output_type=None):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph

    if index == 0:
        #Last One Month
        data_x = [x for x in range(30, 0, -1)]
    elif index == 1:
        #Next 10 days
        data_x = [x for x in range(11)]

    if state:
        #GET Data for Data
        print(state, district, output_type)
        if index == 0:
            #Last One Month
            data_y = [random.randint(0, y) for y in range(30)]
        elif index == 1:
            #Next 10 days
            data_y = [random.randint(0, y) for y in range(10)]
    else:
        if index == 0:
            #Last One Month
            data_y = [random.randint(0, y) for y in range(30)]
        elif index == 1:
            #Next 10 days
            data_y = [random.randint(0, y) for y in range(10)]


    return generate_metric_row(
        div_id,

        None,

        {
            "id": item,
            "className": "metric-row-button-text",
            "children": html.Button(
                id=button_id,
                className="metric-row-button",
                children=item,
                title="Click to visualize live parameter chart",
                n_clicks=0,
            ),
        },

        {
            "id": item + "_sparkline",
            "children": dcc.Graph(
                id=sparkline_graph_id,
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": data_x,
                                "y": data_y,
                                "mode": "lines+markers",
                                "name": item,
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },
    )

def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Parameter")},
        {"id": "m_header_3", "children": html.Div("Sparkline")}
    )

def build_right_panel():
    return html.Div(
        id="status-container",
        # className="row",
        children=[
            # Metrics summary
                    html.Div(
                        id="quick-stats",
                        className="twelve columns",
                        children=[
                            generate_section_banner("Put a heading here"),
                            # Choose State
                            drc.NamedDropdown(
                                name="Select State",
                                id="dropdown-select-state",
                                options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                                clearable=False,
                                searchable=True,
                                value="AP",
                            ),

                            drc.NamedDropdown(
                                name="Select State",
                                id="dropdown-select-district",
                                # options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                                options= [ {"label" : i, "value" : i} for i in state_districts_data['states'][0]['districts'] ],
                                clearable=False,
                                searchable=True,
                                value="Anantapur",
                            ),

                            dcc.RadioItems(
                                id='radio-output-type',
                                options=[
                                    {'label': 'New Cases', 'value': 'NC'},
                                    {'label': 'Recovered', 'value': 'RC'},
                                    {'label': 'Vaccinated', 'value': 'VC'}
                                ],
                                value='NC'
                            )
                        ]
                    ),

            # html.Div(
            #     className="row",
                # children=[
                    html.Div(
                        id="ooc-geomap-outer",
                        className="twelve columns",
                        children=[
                            generate_section_banner("Map Spec"),
                            html.Div(
                                id="geo-map-loading-outer",
                                children=[
                                    dcc.Loading(
                                        id="loading",
                                        children=dcc.Graph(
                                            id="geo-map",
                                            figure={
                                                "data": [],
                                                "layout": dict(
                                                    plot_bgcolor="#171b26",
                                                    paper_bgcolor="#171b26",
                                                ),
                                            },
                                        ),
                                    )
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        id="metric-summary-session",
                        className="twelve columns",
                        children=[
                            generate_section_banner("CoVID-19 Vaccine metrics Summary"),
                            html.Div(
                                id="metric-div",
                                children=[
                                    generate_metric_list_header(),
                                    html.Div(
                                        id="metric-rows",
                                        children=[
                                            generate_metric_row_helper(0),
                                            generate_metric_row_helper(1),
                                            # generate_metric_row_helper(2),
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                # ]
            # )
        ]
    )
                
def build_tab_1():
    return [

        html.Div(
            id="set-specs-intro-container",
            children=html.P(
                "Set your parameters for Herd Immunity"
            )
        ),

        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="value-setter-menu",
                    children=[
                        html.Div(
                            id="value-setter-panel",
                            children=[
                                html.Div(
                                    className='row',
                                    children=[
                                        html.Div(
                                            className='six columns',
                                            children=[
                                                drc.NamedSlider(
                                                    name="Set the threshold for number of cases",
                                                    id="slider-threshold-perc",
                                                    min=0,
                                                    max=15,
                                                    marks={
                                                        i: str(i)
                                                        for i in range(0, 16, 5)
                                                    },
                                                    step=5,
                                                    value=5,
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className='six columns',
                                            children=[
                                                drc.NamedSlider(
                                                    name="Select the number of days",
                                                    id="slider-num-days",
                                                    min=0,
                                                    max=15,
                                                    marks={
                                                        i: str(i)
                                                        for i in range(0, 16, 3)
                                                    },
                                                    step=3,
                                                    value=3,
                                                )
                                            ],
                                        )
                                    ]
                                ),
                                html.Br(),
                                html.Div(
                                    className='twelve columns',
                                    children=[
                                        html.H3(id='slider-output')
                                    ]
                                )
                            ]
                        ),
                        # html.Br(),
                        # html.Div(
                        #     id="button-div",
                        #     children=[
                        #         html.Button("Update", id="value-setter-set-btn")
                        #     ]
                        # )
                    ]
                )
            ]
        )
    ]

def build_tab_2():
    pass

def build_tab_3():
    return html.Div(
        children=[
            drc.NamedSlider(
                name="Select % of population to vaccinate",
                id="slider-vac-perc",
                min=0,
                max=100,
                marks={
                    i: str(i)
                    for i in range(0, 101, 10)
                },
                step=10,
                value=10,
            ),
            dcc.Graph(
                id='vac-graph'
            )
        ]
    )
                     
def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Specification Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Control Charts Dashboard",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Statistics-tab",
                        label="Statistics Dashboard",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

#--------------------------------------------------------------------
#                         Map Generator
#--------------------------------------------------------------------

def generate_map(geo_map_json = india_gj, geo_dataframe = india_data, state_select = None):
    
    with open(geo_map_json, 'r') as fp:
        geo_map = json.load(fp)

    trace = go.Choroplethmapbox(geojson=geo_map,
                                featureidkey='properties.district',
                                locations=geo_dataframe.loc[:, 'District'],
                                z=geo_dataframe.loc[:, 'Active Cases'], 
                                zmin=0,
                                zmax=1000,
                                colorscale='YlOrRd',
                                colorbar=dict(title='Cases',
                                            len=0.8,
                                            lenmode='fraction'))

    traces = []
    traces.append(trace)

    layout = go.Layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        plot_bgcolor="#171b26",
        paper_bgcolor="#171b26",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=10,
            style='dark',
            center=go.layout.mapbox.Center(
                lat=state_map[state_select]["lat"], lon=state_map[state_select]["long"]
            ),
            pitch=5,
            zoom=state_map[state_select]["zoom"]
        ),
    )
    
    return {"data": traces, "layout": layout}


#--------------------------------------------------------------------
#                           Callbacks
#--------------------------------------------------------------------

#----------------------
#      Tab-1
#----------------------

@app.callback(
    Output("slider-output", 'children'),
    inputs=[
        Input('slider-threshold-perc', 'value'),
        Input('slider-num-days', 'value')
    ]
)
def calculate_herd_immunity(threshold, days):

    # Add function and hardcode data here

    result = f"Number of cases less than {threshold} for {days} days is ANSWER"
    return result


#----------------------
#      Tab-2
#----------------------

@app.callback(
    Output("dropdown-select-district", "options"),
    Input("dropdown-select-state", "value")
)
def dropdown_district(state_name):
    state_name = state_map[state_name]['state']
    for state in state_districts_data['states']:
        # print(state['state'])
        # print(state_name)
        if state['state'] == state_name:
            # print(type(state['districts']))
            return [ { "label" : str(i), "value" : str(i) } for i in state['districts'] ]


@app.callback(
    Output('metric-rows', 'children'),
    Input('dropdown-select-district', 'value'),
    Input('radio-output-type', 'value'),
    State('dropdown-select-state', 'value')
)
def update_graphs(district, output_type, state):

    children = [
        generate_metric_row_helper(0, state, district, output_type),
        generate_metric_row_helper(1, state, district, output_type)
    ]
    return children


#----------------------
#      Tab-3
#----------------------
@app.callback(
    Output('vac-graph', 'figure'),
    Input('slider-vac-perc', 'value'),
    # State('dropdown-select-state', 'value'),
    # State('radio-output-type', 'value')
)
def predict_vacc_effect(perc, state=None, district=None):
    print('LOL Triggered')
    x = [i for i in range(100)]
    y = [random.randint(0, i) for i in range(100)]
    df = pd.DataFrame( {'day' : x, 'cases' : y} )

    fig = px.line(
        df,
        x='day',
        y='cases',
        title=f"Cases in {district}, {state} after vaccinating {perc}% of the population",
    )

    fig.update_layout(transition_duration=100)

    return fig




# rate_input = daq.NumericInput(
#     id="rate_input", className="setting-input", size=200, max=9999999
# )
# days_input = daq.NumericInput(
#     id="days_input", className="setting-input", size=200, max=9999999
# )

# @app.callback(
#     output=[
#         Output("value-setter-panel", "children"),
#         Output("rate_input", "value"),
#         Output("days_input", "value")
#     ],
#     inputs=[Input("metric-select-dropdown", "value")],
#     state=[State("value-setter-store", "data")],
# )
# def build_value_setter_panel(dd_select, state_value):
#     return (
#         [
#             build_value_setter_line(
#                 "value-setter-panel-header",
#                 "Parameter",
#                 "Default Value",
#                 "Set new value",
#             ),
#             build_value_setter_line(
#                 "value-setter-panel-rate",
#                 "Rate of Vaccination(%)",
#                 50,
#                 rate_input,
#             ),
#             build_value_setter_line(
#                 "value-setter-panel-days",
#                 "Lower Specification limit",
#                 2,
#                 days_input,
#             )
#         ],
#         state_value['rate'],
#         state_value['days']
#     )

# data = {}
# data['rate'] = 50
# data['days'] = 1
# @app.callback(
#     output=Output("value-setter-store", "data"),
#     inputs=[Input("value-setter-set-btn", "n_clicks")],
#     state=[
#         State("metric-select-dropdown", "value"),
#         State("value-setter-store", "data"),
#         State("rate_input", "value"),
#         State("days_input", "value"),
#     ],
# )
# def set_value_setter_store(set_btn, param, data, rate, days):
#     if set_btn is None:
#         return data
#     else:
#         data[param]["rate"] = rate
#         data[param]["days"] = days
#         return data


@app.callback(
    Output("app-content", "children"),
    [Input("app-tabs", "value")]
)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return build_tab_1()
    elif tab_switch == "tab2":
        return html.Div(
            id="status-container",
            children=[
                # build_left_panel(),
                # html.Div(
                #     id="graphs-container",
                #     children=[build_right_panel()],
                # )
                build_right_panel()
            ]
        )
    else:
        return build_tab_3()

@app.callback(
    Output("geo-map", "figure"),
    [Input("dropdown-select-state", "value")]
)
def update_geo_map(state_select):
    state_agg_data = data_dict[state_select]
    map_gj = gj_dict[state_select]
    return generate_map(map_gj, state_agg_data, state_select)

#----------------------
#      Tab-3
#----------------------


#----------------------
#      Others
#----------------------

@app.callback(
    Output("markdown", "style"),
    [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")],
)
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {"display": "none"}

#--------------------------------------------------------------------
#                            Layout
#--------------------------------------------------------------------

app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        build_modal(),
    ],
)

#--------------------------------------------------------------------
#                           App Runner
#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True, port=8069)