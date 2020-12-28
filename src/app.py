import flask
from flask_caching import Cache

import ipywidgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate

import pandas as pd

import json
import os

#--------------------------------------------------------------------
#                        Load Configs
#--------------------------------------------------------------------

with open('../config.json') as config_file:
    config = json.load(config_file)

mapbox_access_token = config['mapbox-token']
# mapbox_style = config['mapbox_style']
px.set_mapbox_access_token(mapbox_access_token)

#--------------------------------------------------------------------
#                       Initialise App
#--------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets = [
        'https://codepen.io/chriddyp/pen/bWLwgP.css'
    ],
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

server = app.server

app.config["suppress_callback_exceptions"] = True


#--------------------------------------------------------------------
#                           Load files
#--------------------------------------------------------------------

state_map = {
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

# Load national and statewise data
india_data = pd.read_csv('../data/prediction_india.csv')

data_dict = {}
for state in state_list:
    p = os.getcwd().split(os.path.sep)
    csv_path = "../data/state_data/prediction_{}.csv".format(state)
    state_data = pd.read_csv(csv_path)
    data_dict[state] = state_data

# Load GeoJsons

# Change this to state and change the entire logic later
india_gj = "../maps/india_districts.geojson"

gj_dict = {}
for state in state_list:
    p = os.getcwd().split(os.path.sep)
    geojson_path = "../maps/{}.geojson".format(state)
    gj_dict[state] = geojson_path

#--------------------------------------------------------------------
#                         Layout Helpers
#--------------------------------------------------------------------

def build_left_panel():
    return html.Div(
        id="left",
        className="six columns",
        children=[

            # Heading
            html.P(
                className="section-title",
                children="Choose the districts on the map to get statistics",
            ),

            # Choose State
            html.Div(
                className="control-row-1",
                children=[
                    html.Div(
                        id="state-select-outer",
                        children=[
                            html.Label("Select a State"),
                            dcc.Dropdown(
                                id="state-select",
                                options=[{"label": i, "value": i} for i in state_list],
                                value=state_list[1],
                            ),
                        ],
                    ),
                ],
            ),
            # Summary Table
            # Might need to update this part with visualisations
        ]
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
                                colorscale='Viridis',
                                colorbar=dict(title='Cases',
                                            len=0.8,
                                            lenmode='fraction'))

    traces = []
    traces.append(trace)

    layout = go.Layout(
        margin=dict(l=10, r=10, t=20, b=10, pad=5),
        # plot_bgcolor="#171b26",
        # paper_bgcolor="#171b26",
        clickmode="event+select",
        hovermode="closest",
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=state_map[state_select]["lat"], lon=state_map[state_select]["long"]
            ),
            pitch=5,
            zoom=state_map[state_select]["zoom"],
            style="white-bg",
        ),
    )
    
    return {"data": traces, "layout": layout}


#--------------------------------------------------------------------
#                         Visualisation
#--------------------------------------------------------------------

app.layout = html.Div(
    className="container scalable",
    children=[
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.H6("CoVID-19 India Predictor"),
            ],
        ),

        html.Div(
            id="upper-container",
            className="row",
            children=[
                # Build the analysis panel
                build_left_panel(),

                # Map Analysis
                html.Div(
                    id="geo-map-outer",
                    className="six columns",
                    children=[
                        html.P(
                            id="map-title",
                            children="Predicted CoVID cases State of {}".format(
                                state_map[state_list[1]]["state"]
                            ),
                        ),
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
            ],
        ),
    ],
)

#--------------------------------------------------------------------
#                         Callbacks
#--------------------------------------------------------------------

@app.callback(
    Output("geo-map", "figure"),
    [    
        Input("state-select", "value"),
    ],
)
def update_geo_map(state_select):
    state_agg_data = data_dict[state_select]
    map_gj = gj_dict[state_select]
    return generate_map(map_gj, state_agg_data, state_select)


@app.callback(
    Output("map-title", "children"),
    [Input("state-select", "value")],
)
def update_region_dropdown(state_select):
    return ("Predicted CoVID cases State of {}".format(state_map[state_select]["state"]))


# trace = go.Choroplethmapbox(geojson=ind_dis,                            
#                             featureidkey='properties.district',
#                             locations=future.loc[:, 'District'],
#                             z=future.loc[:, 'Active Cases'], 
#                             zmin=0,
#                             zmax=500,
#                             colorscale='Viridis',
#                             colorbar=dict(title='Total Active Cases in India',
#                                           len=0.8,
#                                           lenmode='fraction'))

# lyt = dict(title='Total Active Cases in India',
#            height=700,
#            mapbox_zoom=3.4,
#            mapbox_center={'lat': 20.5937, 'lon': 78.9629})

# fig = go.FigureWidget(data=[trace], layout=lyt)

# fig.update_layout(
#     mapbox_accesstoken = mapbox_access_token,
#     mapbox_style = 'dark',
#     plot_bgcolor = colors['background'],
#     paper_bgcolor = colors['background'],
#     font_color = colors['text']
# )

#--------------------------------------------------------------------
#                           App Runner
#--------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)