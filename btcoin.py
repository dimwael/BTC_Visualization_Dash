import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from loremipsum import get_sentences

import os
import numpy as np
import pandas as pd
import pickle
import quandl
from datetime import datetime

def get_quandl_data(quandl_id):
    '''Download and cache Quandl dataseries'''
    cache_path = '{}.pkl'.format(quandl_id).replace('/','-')
    try:
        f = open(cache_path, 'rb')
        df = pickle.load(f)
        print('Loaded {} from cache'.format(quandl_id))
    except (OSError, IOError) as e:
        print('Downloading {} from Quandl'.format(quandl_id))
        df = quandl.get(quandl_id, returns="pandas")
        df.to_pickle(cache_path)
        print('Cached {} at {}'.format(quandl_id, cache_path))
    return df

btc_usd_price_kraken = get_quandl_data('BCHARTS/KRAKENUSD')

app = dash.Dash()

app.scripts.config.serve_locally = True

vertical = True

if not vertical:
    app.layout = html.Div([
        dcc.Tabs(
            tabs=[
                {'label': 'Market Value', 'value': 1},
                {'label': 'Usage Over Time', 'value': 2},
                {'label': 'Predictions', 'value': 3},
                {'label': 'Target Pricing', 'value': 4},
            ],
            value=3,
            id='tabs',
            vertical=vertical
        ),
        html.Div(id='tab-output')
    ], style={
        'width': '80%',
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto'
    })

else:
    app.layout = html.Div([
        html.Div(
            dcc.Tabs(
                tabs=[
                    {'label': 'USD', 'value': 1},
                    {'label': 'EUR', 'value': 2},
                    {'label': 'YEN', 'value': 3},
                    {'label': 'TND', 'value': 4},
                ],
                value=1,
                id='tabs',
                vertical=vertical,
                style={
                    'height': '200vh',
                    'borderRight': 'thin lightgrey solid',
                    'textAlign': 'middle'
                }
            ),
            style={'width': '20%', 'float': 'left'}
        ),
        html.Div(
            html.Div(id='tab-output'),
            style={'width': '80%', 'float': 'right'}
        )
    ], style={
        'fontFamily': 'Sans-Serif',
        'margin-left': 'auto',
        'margin-right': 'auto',
    })


@app.callback(Output('tab-output', 'children'), [Input('tabs', 'value')])
def display_content(value):
    #exchange should be dynamic and updated through exchange ratio with : Exchange = get_quandl_data('FRED/DEXUSEU')
    #But i am using a static ratio token 16-02-2018 for euro / yen / dnt
    exchange = [1,	1.24342,106.191,2.38738]
    exchangeName = ["Dollar", "euro", "Yen", "TD"]
    data = [
        {
            'x': btc_usd_price_kraken.index,
            'y': btc_usd_price_kraken['Weighted Price'] * exchange[int(value)],
            'name': exchangeName[value],
            'marker': {
                'color': 'rgb(55, 83, 109)'
            },
            'type': ['scatter', 'scatter', 'scatter'][int(value) % 3]
        }
    ]

    return html.Div([
        dcc.Graph(
            id='graph',
            figure={
                'data': data,
                'layout': {
                    'margin': {
                        'l': 30,
                        'r': 90,
                        'b': 30,
                        't': 0
                    },
                    'legend': {'x': 0, 'y': 1}
                }
            }
        ),
        #html.Div(' '.join(get_sentences(10)))
        
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
