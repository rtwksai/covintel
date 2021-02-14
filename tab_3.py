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

def build_tab_3():
    return html.Div(
            children=[
                html.Div(
                    id="ooc-geomap-outer",
                    className="twelve columns",
                    children=[
                        # generate_section_banner("Map Spec"),
                        html.H3('Vaccine Distribution Statistics'),
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
                    style={'width': '70%', 'display': 'inline-block', 'border-left': '0'}
                ),
                html.Div(
                    id="vaccine-info",
                    className="twelve columns",
                    children=[
                        # generate_section_banner("CoVID-19 Vaccine Distribution Summary"),
                        html.H3('Vaccine Distribution Details'),
                        html.Div(
                            id="metric-div",
                            children=[
                                html.H2(
                                    "CoVaxin is highly Effective*."
                                ),
                                html.H4(
                                    "Vaccine Rollout Phase 1 in progress"
                                ),
                                html.P(
                                    # "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam consequat tellus ac magna ullamcorper consequat a eget tellus. Maecenas eleifend vel velit non rhoncus. Ut mollis nec justo quis "
                                    # "pharetra. Donec a bibendum lectus, sed tincidunt urna. Vivamus sem odio, pharetra vel nibh in, gravida finibus nisl. Vestibulum tincidunt et odio non eleifend. Ut non purus rhoncus, convallis risus eu,"
                                    # " aliquet magna. Duis varius massa eget massa ultricies venenatis lobortis vel velit. Vivamus sollicitudin ultrices velit sed tristique. Sed luctus lectus at"
                                    # "neque feugiat suscipit in id odio. Aenean commodo purus eu vestibulum lacinia. Morbi dignissim aliquet lacus eu ultricies. Cras nec rutrum orci. Nam sed massa"
                                    # " eu metus lobortis vulputate fermentum at diam. Aliquam tincidunt dolor elementum est tempus feugiat. Curabitur non nunc velit."
                                    "India will start off by vaccinating around three crore of its front-line workers. This includes health workers, safai karmacharis, the Army and disaster management volunteers."
                                ),
                                html.H5(
                                    "Number of Centers providing vaccination : 196"
                                ),
                                html.H6("*All this data has been fetched from CoWIN API.")
                            ]
                        )
                    ],
                    style={'width': '30%', 'display': 'inline-block'}
                ),
                # html.Div(
                #     children=[
                #         html.B(
                #             "To get updates over SMS for vaccine updates in your area. Click the button below."
                #         ),
                #         html.Br(),
                #         html.Button(
                #             "Click to Subscribe",
                #             id="subscribe-button",
                #             style={'margin-top': '1.5rem', 'background-color': 'red', 'color': 'white'}
                #         )
                #     ],
                #     style={'width': '100%', 'display': 'inline-block', 'padding-top': '5rem'}
                # )
            ],
            style={'width': '100%', 'display': 'inline-block', 'padding': '1.5rem 10rem'}
        )
