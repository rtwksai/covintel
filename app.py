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

from utils import dash_reusable_components as drc

import numpy as np
import pandas as pd
import json
import os
import random


from tab_1 import build_tab_1
from tab_2 import build_tab_2, generate_metric_row_helper
from tab_3 import build_tab_3
from tab_4 import build_tab_4
from banner import build_banner
from state_list import *

import base64
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


state_map = get_state_map()
state_list = get_state_list()
state_districts_data = get_state_districts_data()


# Load national and statewise data
india_data = pd.read_csv('./data/state_data/prediction_IN.csv')

data_dict = {}
for state in state_list:
    p = os.getcwd().split(os.path.sep)
    csv_path = "./data/state_data/prediction_{}.csv".format(state)
    state_data = pd.read_csv(csv_path)
    data_dict[state] = state_data

in_spec = pd.read_csv("./data/state_data/prediction_IN.csv")
in_data =  in_spec.groupby("State", as_index=False)['Active Cases'].agg({"Active Cases": "sum"})
in_data["District"] = in_data["State"]
data_dict["IN"] = in_data

# Load GeoJsons

# Change this to state and change the entire logic later
india_gj = "./maps/india_states.geojson"

gj_dict = {}
for state in state_list:
    p = os.getcwd().split(os.path.sep)
    geojson_path = "./maps/{}.geojson".format(state)
    gj_dict[state] = geojson_path


new = get_new()
recover = get_recover()
vaccinated = get_vaccinated()

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

                        Tracking the number of New cases, Deceased cases, and Immune cases as the vaccination process kick-off.  This is followed by predicting the trends of the same for the future. From this, we can gain insight into Drop-in COVID +ve cases and deaths  in States/Region and areas where vaccination has been prevalent the  high-risk areas that require vaccination with high priority the number of potential COVID-19 cases at States/Regions  and areas where vaccination has been prevalent.
 
                    """
                            )
                        ),
                    ),
                ],
            )
        ),
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
                        label="Herd Immunity",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="District wise Statistics",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Statistics-tab",
                        label="Live Vaccine Statistics",
                        value="tab3",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Effectiveness-tab",
                        label="Vaccine Effectiveness",
                        value="tab4",
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

def generate_map(geo_map_json = india_gj, geo_dataframe = india_data, state_select = None, scal="Viridis"):
    
    with open(geo_map_json, 'r') as fp:
        geo_map = json.load(fp)

    trace = go.Choroplethmapbox(geojson=geo_map,
                                featureidkey='properties.district',
                                locations=geo_dataframe.loc[:, 'District'],
                                z=geo_dataframe.loc[:, 'Active Cases'], 
                                zmin=0,
                                zmax=500,
                                colorscale=scal,
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
        Input('slider-num-days', 'value'),
        Input('dropdown-select-district', 'value'),
        State('dropdown-select-state', 'value')
    ]
)
def calculate_herd_immunity(threshold, days, district, state):
    # Add function and hardcode data here

    result = f"For {district}, {state}. Number of cases less than {threshold} for {days} days is 20% progress towards herd immunity"
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
    # Input('radio-output-type', 'value'),
    State('dropdown-select-state', 'value')
)
def update_graphs(district, state):

    output_type = 'NC'
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
    Input('dropdown-select-district', 'value'),
    State('dropdown-select-state', 'value')
)
def predict_vacc_effect(perc, district=None, state=None):
    # print(perc, state, district)

    name = str(district) + "_v" + str(perc)
    # print(name)

    x = [i for i in range(11)]
    y = vaccinated[name]
    df = pd.DataFrame( {'day' : x, 'cases' : y} )
    # graph_title = "Cases in {0}, {1} after vaccinating {2}% of the population".format(district, state, perc)

    title = f"Cases in {district}, {state} after vaccinating {perc}% of the population, using COVAXIN."
    # title="Cases in Chittoor, AP after vaccinating 3% of the population, using CoVaxin."
    # print(perc, state, district, "2")

    fig = px.line(
        df,
        x='day',
        y='cases',
        title=title,
    )

    fig.update()

    return fig

@app.callback(
    Output("app-content", "children"),
    [Input("app-tabs", "value")]
)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return build_tab_1()
    elif tab_switch == "tab2":
        return build_tab_2()
    elif tab_switch == "tab3":
        return build_tab_3()
    else:
        return build_tab_4()

@app.callback(
    Output("geo-map", "figure"),
    [Input("dropdown-select-state", "value"), Input("app-tabs", "value")]
)
def update_geo_map(state_select, tab_switch):
    state_agg_data = data_dict[state_select]
    map_gj = gj_dict[state_select]
    if tab_switch == "tab2":
        scal="YlOrRd"
    elif tab_switch == "tab3":
        scal="Sunset"
    else:
        scal="Sunset"
    return generate_map(map_gj, state_agg_data, state_select, scal)

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
    app.run_server(debug=True, port=8080, host='0.0.0.0')




