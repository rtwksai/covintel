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

from state_list import *

state_list = get_state_list()
state_map = get_state_map()
state_districts_data = get_state_districts_data()

new = get_new()
recover = get_recover()
vaccinated = get_vaccinated()

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_tab_2():
    return html.Div(
        id="status-container",
        # className="row",
        children=[
            # Metrics summary
            html.Div(
                children=[
                    html.Div(
                        id="ooc-geomap-outer",
                        className="twelve columns",
                        children=[
                            # generate_section_banner("Map Spec"),
                            html.H3('Recorded & Predicted Daily New Cases'),
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
                                                    plot_bgcolor="#ffffff",
                                                    paper_bgcolor="#ffffff",
                                                ),
                                            },
                                        ),
                                    )
                                ],
                            ),
                        ],
                        style={'width': '50%', 'height': 'inherit', 'display': 'inline-block', 'border-left': '0'}
                    ),
                    html.Div(
                        id="metric-summary-session",
                        className="twelve columns",
                        children=[
                            # generate_section_banner("CoVID-19 Vaccine metrics Summary"),
                            # html.H3('')
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
                        ],
                        style={'width': '50%', 'display': 'inline-block'}
                    ),
                ],
                style={'width': '100%', 'display': 'inline-block', 'padding': '1.5rem 5rem'}
            )
        ]
    )

params = ['Daily New Cases', 'Daily Recovered Cases']
suffix_row = "_row"
suffix_button_id = "_button"
suffix_sparkline_graph = "_sparkline_graph"

def generate_metric_row_helper(index, state=None, district=None, output_type=None):
    item = params[index]

    #print('INDEX' + str(index) + str(output_type))

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph

    data_y_1 = ['NOT ASSIGNED']
    data_y_2 = ['NOT ASSIGNED']


    data_x_1 = [x for x in range(31)]
    data_x_2 = [c for c in range(30, 40)]

    if state:
        #GET Data for Data
        # print(state, district, output_type)
        # if index == 0:
            #Last One Month
        if output_type=='NC':
            # name = state + "_30"
            combined_data = new[state + "_30"] + new[state + "_10"]
            data_y_1 = combined_data[:31]
            data_y_2 = combined_data[30:40]
            # data_y = combined_data
        elif output_type=='RC':
            combined_data = recover[state + "_30"] + recover[state + "_10"]
            # data_y = combined_data
            data_y_1 = combined_data[:31]
            data_y_2 = combined_data[30:40]

        # elif index == 1:
        #     #Next 10 days
        #     if output_type=='NC':
        #         name = state + "_10"
        #         data_y = new[name]
        #     elif output_type=='RC':
        #         name = state + "_10"
        #         data_y = recover[name]
        #     # data_y = [random.randint(0, y) for y in range(10)]
        # else:
        #     data_y = [random.randint(0, y) for y in range(40)]
            
    else:
        if index == 0:
            #Last One Month
            data_y = [random.randint(0, y) for y in range(10)]
        elif index == 1:
            #Next 10 days
            data_y = [random.randint(0, y) for y in range(40)]
        else:
            data_y = [random.randint(0, y) for y in range(40)]
    #print('LOL')
    #print(data_y)
    #print('LOL2')

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
                style={"width": "100%", "height": "100%"},
                config={
                    "staticPlot": True,
                    "editable": True,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": data_x_1,
                                "y": data_y_1,
                                "mode": "lines+markers",
                                "name": item,
                                "line": {"color": "#ff9933"},
                            },
                            {
                                "x": data_x_2,
                                "y": data_y_2,
                                "mode": "lines+markers",
                                "name": item + "_",
                                "line": {"color": "#4df4ea"},
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
                            "showlegend": False
                        },
                    }
                ),
            ),
        },
    )

def generate_metric_row(id, style, col1, col2):
    if style is None:
        style = {"height": "15rem", "width": "100%"}

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

def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Cases")},
        {"id": "m_header_3", "children": html.Div("Trends")}
    )
