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
            # html.Div(
            #     children=[
            #         drc.NamedSlider(
            #             name="Select % of population to vaccinate",
            #             id="slider-vac-perc",
            #             min=0,
            #             max=15,
            #             marks={
            #                 i: str(i)
            #                 for i in [0, 1, 3, 5, 9]
            #             },
            #             step=1,
            #             value=1,
            #         ),
            #     ],
            # ),
            html.H3("Predictions vs Actual Number of Cases"),
            html.Div(
                children=[
                    html.Div(
                        children=[
                            dcc.Graph(
                                id='vac-graph'
                            )
                        ],
                        style={'width': '70%', 'display': 'inline-block', 'padding-right': '1rem'}
                    ),
                    html.Div(
                        children=[
                            html.H2('Highlights'),
                            html.H4("Vaccine has underperformed in Chittoor, Andhra Pradesh!"),
                            html.H4("Reasons could be:"),
                            html.Li(html.H5("A new strain of Virus could be a possibility")),
                            html.Li(html.H5("Poor immune response in the people")),
                            html.Li(html.H5("High density of comorbid people")),
                            # html.H5("")
                        ],
                        style={'width': '30%', 'display': 'inline-block', 'padding-left': '2rem','text-align': 'top' }
                    )
                ]
            ),
            # html.Div(
            #     children=[
            #         html.H2('Pro Level Analysis'),
            #         html.P("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam consequat tellus ac magna ullamcorper consequat a eget tellus. Maecenas eleifend vel velit non rhoncus. Ut mollis nec justo quis "
            #                 "pharetra. Donec a bibendum lectus, sed tincidunt urna. Vivamus sem odio, pharetra vel nibh in, gravida finibus nisl. Vestibulum tincidunt et odio non eleifend. Ut non purus rhoncus, convallis risus eu,"
            #                 " aliquet magna. Duis varius massa eget massa ultricies venenatis lobortis vel velit. Vivamus sollicitudin ultrices velit sed tristique. Sed luctus lectus at"
            #                 "neque feugiat suscipit in id odio. Aenean commodo purus eu vestibulum lacinia. Morbi dignissim aliquet lacus eu ultricies. Cras nec rutrum orci. Nam sed massa")
            #     ]
            # )
        ],
        style={'padding': '5rem 10rem'}
    )
