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

import base64

from state_list import *

state_list = get_state_list()
state_map = get_state_map()
state_districts_data = get_state_districts_data()
vaccine_list = get_vaccine_list()

logo_png = 'assets/chaos.png'
logo_base64 = base64.b64encode(open(logo_png, 'rb').read()).decode('ascii')



def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                children=[
                    html.Div(
                        id="banner-text",
                        children=[
                            html.H5("Monitoring CoVID-19 Vaccine campaign"),
                            # html.H6("Vaccine efficacy and herd immunity predictor"),
                            # html.H2('CovIntel', style={'font-family' : "'Raleway', sans-serif", 'font-weight' : '900', 'margin-bottom' : '0'})
                        ],
                        style={'width': '50%', 'display': 'inline-block'}
                    ),
                    html.Div(
                        id="banner-logo",
                        children=[
                            html.Button(
                                id="learn-more-button", children="LEARN MORE", n_clicks=0, style={'display' : 'none'}
                            ),
                            # html.Img(id="logo", src=""),
                            # html.Img(src='data:image/png;base64,{}'.format(logo_base64), style={'margin-bottom' : '0.5rem'}),
                            html.H2('CovIntel', style={'font-family' : "'Raleway', sans-serif", 'font-weight' : '900', 'margin-bottom' : '0'})
                        ],
                        style={'width': '50%', 'display': 'inline-block', 'text-align': 'right'}
                    )
                ]
            ),
            html.Div(
                id="banner-select-location",
                # className="twelve columns",
                children=[

                        # generate_section_banner(),
                        # html.Div(
                        #     className='section-banner',
                        #     children="Select a State, District & Vaccine",
                        #     style={'text-align': 'center'}
                        # ),
                        html.Hr(
                            style={'margin-top':'0.2rem', 'margin-bottom':'0.5rem'}
                        ),
                        # Choose State
                        html.Div(
                            drc.NamedDropdown(
                                name="Select State",
                                id="dropdown-select-state",
                                options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                                clearable=False,
                                searchable=True,
                                value="AP",
                            ),
                            style={'width': '40%', 'display': 'inline-block'}
                        ),
                        html.Div(
                            drc.NamedDropdown(
                                name="Select District",
                                id="dropdown-select-district",
                                # options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                                options= [ {"label" : i, "value" : i} for i in state_districts_data['states'][0]['districts'] ],
                                clearable=False,
                                searchable=True,
                                value="Chittoor",
                            ),
                            style={'width': '30%', 'display': 'inline-block'}
                        ),
                        html.Div(
                            drc.NamedDropdown(
                                name="Select Vaccine",
                                id="dropdown-select-vaccine",
                                # options=[{"label": state_map[i]["state"], "value": i} for i in state_list],
                                options= [ {"label" : i, "value" : i} for i in vaccine_list ],
                                clearable=False,
                                searchable=True,
                                value="Chittoor",
                            ),
                            style={'width': '30%', 'display': 'inline-block'}
                        )
                    ],
                    style={'width': '100%', 'display': 'inline-block'}
                ),
        ],
        style={'width': '100%', 'display': 'inline-block'}
    )