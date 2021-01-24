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

from state_list import get_state_list, get_state_map, get_state_districts_data

state_list = get_state_list()
state_map = get_state_map()
state_districts_data = get_state_districts_data()

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_tab_4():
    return html.Div(
        children=[
            html.Div(
                children=[
                    drc.NamedSlider(
                        name="Select % of population to vaccinate",
                        id="slider-vac-perc",
                        min=0,
                        max=90,
                        marks={
                            i: str(i)
                            for i in [0, 10, 30, 50, 90]
                        },
                        step=10,
                        value=10,
                    ),
                ],
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id='vac-graph'
                    )
                ]
            )
        ],
        style={'padding': '5rem 10rem'}
    )