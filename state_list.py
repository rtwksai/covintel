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

state_map = {
    "IN": {"state": "India", "lat": 20.5937, "long": 78.9629, "zoom": 3},
    "AN": {"state": "Andaman and Nicobar Islands", "lat": 12.698214530944824, "long": 92.85771179199219, "zoom": 5},
    "AP": {"state": "Andhra Pradesh", "lat": 15.9240905, "long": 80.1863809, "zoom": 5},
    "AR": {"state": "Arunachal Pradesh", "lat": 28.0937702, "long": 94.5921326, "zoom": 5.5},
    "AS": {"state": "Assam", "lat": 26.4073841, "long": 93.2551303, "zoom": 5},
    "BR": {"state": "Bihar", "lat": 25.6440845, "long": 85.906508, "zoom": 5.3},
    "CG": {"state": "Chandigarh", "lat": 30.7334421, "long": 76.7797143, "zoom": 10},
    "CT": {"state": "Chhattisgarh", "lat": 21.295132, "long": 81.828232, "zoom": 5.1},
    "DN": {"state": "Dadra and Nagar Haveli and Daman and Diu", "lat": 20.7179857, "long": 70.9323992, "zoom": 5.5},
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
    "OR": {"state": "Odisha", "lat": 20.940920, "long": 84.803467, "zoom": 5},
    "PY": {"state": "Puducherry", "lat": 11.941552, "long": 79.808289, "zoom": 8},
    "PB": {"state": "Punjab", "lat": 31.147129, "long": 75.341217, "zoom": 6.2},
    "RJ": {"state": "Rajasthan", "lat": 27.891277, "long": 74.432617, "zoom": 4.5},
    "SK": {"state": "Sikkim", "lat": 27.606001, "long": 88.473167, "zoom": 5},
    "TN": {"state": "Tamil Nadu", "lat": 11.059821, "long": 78.387451, "zoom": 5},
    "TG": {"state": "Telangana", "lat": 17.123184, "long": 79.208824, "zoom": 5},
    "TR": {"state": "Tripura", "lat": 23.745127, "long": 23.745127, "zoom": 5},
    "UP": {"state": "Uttar Pradesh", "lat": 26.244156, "long": 92.537842, "zoom": 5},
    "UT": {"state": "Uttarakhand", "lat": 30.379910, "long": 78.877386, "zoom": 6},
    "WB": {"state": "West Bengal", "lat": 23.578624, "long": 87.747803, "zoom": 5},
}

with open('./data/states-and-districts.json') as dist_json:
    state_districts_data = json.load(dist_json)


def get_state_map():
    return state_map

def get_state_list():
    return list(state_map.keys())

def get_state_districts_data():
    return state_districts_data
    


# DATA

# Percentage Population Vaccinated
vaccinated = {
    'Bengaluru (Bangalore) Urban_v0' : [403, 433, 417, 330, 310, 265, 289, 340, 316, 317, 344],
    'Bengaluru (Bangalore) Urban_v10' : [403, 433, 417, 330, 310, 254, 279, 324, 302, 313, 323],
    'Bengaluru (Bangalore) Urban_v30' : [329, 405, 348, 310, 263, 215, 266, 285, 263, 273, 284],
    'Bengaluru (Bangalore) Urban_v50' : [63, 105, 72, 77, 80, 69, 75, 102, 66, 63, 68],
    'Bengaluru (Bangalore) Urban_v90' : [0, 31, 7, 16, 38, 21, 26, 48, 12, 5, 4],
    'Chittoor_v0' : [50, 46, 53, 44, 30, 27, 20, 22, 26, 24, 23],
    'Chittoor_v10' : [34, 35, 36, 32, 22, 22, 13, 19, 21, 19, 16],
    'Chittoor_v30' : [34, 35, 36, 32, 22, 22, 13, 16, 18, 19, 16],
    'Chittoor_v50' : [8, 9, 11, 7, 6, 4, 5, 3, 3, 2, 3],
    'Chittoor_v90' : [2, 1, 2, 0, 1, 0, 2, 2, 0, 0, 0]
}

# Next 10 day recover / new
recover = {
    'KA_10' : [347763.0 ,347555.0 ,347608.0 ,346345.0 ,347555.0 ,347555.0 ,347555.0 ,347555.0 ,347555.0 ,347555.0 ],
    'AP_10' : [85571.0 ,85623.0 ,85623.0 ,85623.0 ,85623.0 ,85392.0 ,85392.0 ,85392.0 ,85392.0 ,85392.0 ,],
    'KA_30' : [351497, 354004, 358553, 359801, 360724, 362231, 363807, 364787, 365578, 366445,
             366888, 368502, 368992, 369701, 370386, 371081, 371879, 372479, 372970, 373724,
             374378, 375221, 375985, 376835, 377443, 377906, 378208, 378936, 378936],
    'AP_30' : [83054, 83151, 83216, 83318, 83420, 83519, 83630, 83667, 83774, 83855, 83997, 84092,
        84177, 84287, 84322, 84392, 84466, 84530, 84612, 84643, 84770, 84811, 84886, 84972,
        85038, 85087, 85141, 85233, 85262]
}

new = {
    'KA_10' : [234.0 ,206.0 ,335.0 ,219.0 ,210.0 ,206.0 ,155.0 ,119.0 ,100.0 ,75.0],
    'AP_10' : [51.0 ,54.0 ,55.0 ,55.0 ,53.0 ,53.0 ,52.0 ,52.0 ,52.0 ,52.0],
    'KA_30' : [638, 728, 701, 659, 606, 672, 369, 673, 676, 689, 687, 586, 659, 363,
            585, 550, 642, 578, 471, 542, 309, 370, 554, 554, 464, 343, 464, 298,
            300],
    'AP_30' : [ 76,  76,  95, 108,  89, 104,  43,  88,  89, 130,  98,  87,  80,  46,
        86,  64,  54,  81,  39, 105,  42,  52,  50,  65,  44,  59,  56,  21,
        82]
}

vaccine_list = ['CoVaxin', 'CoviShield']

def get_new():
    return new

def get_recover():
    return recover

def get_vaccinated():
    return vaccinated

def get_vaccine_list():
    return vaccine_list