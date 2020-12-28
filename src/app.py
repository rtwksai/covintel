import flask
from flask_caching import Cache

import ipywidgets
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd

import json

server = flask.Flask(__name__)

app = dash.Dash(
    __name__,
    server = server,
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
            "content": "width=device-width, initial-scale=1.0"
        }
    ]
)

future = pd.read_csv('../data/prediction.csv')

with open('../maps/india_districts.geojson', 'r') as fp:
    ind_dis = json.load(fp)

trace = go.Choroplethmapbox(geojson=ind_dis,
                            featureidkey='properties.district',
                            locations=future.loc[:, 'District'],
                            z=future.loc[:, 'Active Cases'], 
                            zmin=0,
                            zmax=500,
                            colorscale='Viridis',
                            colorbar=dict(title='Total Active Cases in India',
                                          len=0.8,
                                          lenmode='fraction'))

lyt = dict(title='Total Active Cases in India',
           height=700,
           mapbox_style='white-bg',
           mapbox_zoom=3.4,
           mapbox_center={'lat': 20.5937, 'lon': 78.9629})

fig = go.FigureWidget(data=[trace], layout=lyt)


app.layout = html.Div(children=[
    
    html.Div(children='''
        CoVID-19 India Prediction
    '''),

    dcc.Graph(
        id='india-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)