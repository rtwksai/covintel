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

def build_tab_1():
    return [
        html.Div(
            id="herd-immunity-definition",
            children=[
                html.B('Definition of Herd Immunity'),
                html.P(
                    # "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam consequat tellus ac magna ullamcorper consequat a eget tellus. Maecenas eleifend vel velit non rhoncus. Ut mollis nec justo quis "
                    # "pharetra. Donec a bibendum lectus, sed tincidunt urna. Vivamus sem odio, pharetra vel nibh in, gravida finibus nisl. Vestibulum tincidunt et odio non eleifend. Ut non purus rhoncus, convallis risus eu,"
                    # " aliquet magna. Duis varius massa eget massa ultricies venenatis lobortis vel velit. Vivamus sollicitudin ultrices velit sed tristique. Sed luctus lectus at"
                    # "neque feugiat suscipit in id odio. Aenean commodo purus eu vestibulum lacinia. Morbi dignissim aliquet lacus eu ultricies. Cras nec rutrum orci. Nam sed massa"
                    # " eu metus lobortis vulputate fermentum at diam. Aliquam tincidunt dolor elementum est tempus feugiat. Curabitur non nunc velit."
                    "Resistance to the spread of an infectious disease within a population that is based on pre-existing immunity of a high proportion of individuals as a result of previous infection or vaccination."
                    "Though herd immunity is defined as no new cases for a threshold n days, this seems to be quite impossible in the current scenario. Therefore, our solution allows users to set their own definition of herd immunity.  The definition includes, no. of days - n, threshold no. of cases - c. and the herd immunity % is calculated by, No. of days out of n for which the predicted new cases are less then c/n * 100"

                )
            ],
            style={'margin': '5rem 10rem'}
        ),
        html.Div(
            id="set-specs-intro-container",
            children=html.P(
                "Set your parameters for Herd Immunity"
            ),
            style={'margin': '1.5rem 10rem'}
        ),
        html.Div(
            id="herd-immunity-panel",
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
            ],
            style={'margin': '1.5rem 10rem'}
        ),
        html.Div(
            id="herd-immunity-results",
            children=html.B(
                "Predictions for Herd Immunity"
            ),
            style={'margin': '0.5rem 10rem'}
        ),
        html.Div(
            className='twelve columns',
            children=[
                html.P(id='slider-output')
            ],
            style={'margin': '0rem 10rem'}
        )
    ]