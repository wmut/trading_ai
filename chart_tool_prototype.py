import dash
from dash import dcc as dcc
from dash import html as html
from dash.dependencies import Input, Output
from dash import Dash
import plotly.graph_objects as go

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly_express as px
import itertools

# Helper function to fetch some Yfinance datetime
def generate_plot():
    # Define the ticker symbol for Bitcoin in USD
    ticker = 'BTC-USD'

    # Fetch historical data starting from January 1, 2020
    btc_data = yf.download(ticker, start='2025-01-01', end='2025-03-06', interval='1h')

    # prepare dataframe of long format
    df = btc_data["Close"]
    df["date"] = btc_data.index
    print(df.head())

    return df

df = generate_plot()

# Some plotly magic
fig = px.line(df, x="date", y="BTC-USD", title='BTC-USD')

drawn_shapes_format1 = {"drawdirection": "vertical",
                       "color": "blue",
                       "line": {"width": 1}}

drawn_shapes_format2 = {"drawdirection": "vertical",
                       "layer": "below",
                       "fillcolor": "red",
                       "opacity": 0.51,
                       "line": {"width": 0}}

drawn_shapes_format3 = {"drawdirection": "free",
                       "color": "blue",
                       "line": {"width": 1}}

fig.update_layout(clickmode='event+select', dragmode='drawrect',
                  newshape=drawn_shapes_format2,
                  yaxis=dict(fixedrange=True),
                  xaxis=dict(fixedrange=True))

menus = list([dict(type='buttons', buttons=list([dict(label='marker',
                                                      method='relayout',
                                                      args=[{'dragmode':'drawline', 'newshape': drawn_shapes_format1}]),
                                                 dict(label='line',
                                                      method='relayout',
                                                      args=[{'dragmode':'drawline', 'newshape': drawn_shapes_format3}]
                                                      ),
                                                 dict(label='rectangle',
                                                      method='relayout',
                                                      args=[{'dragmode':'drawrect', 'newshape': drawn_shapes_format2}]
                                                      )
                                                  ])
                    )
              ])
fig.update_layout(updatemenus=menus)

fig.update_traces(marker_size=20)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Dash app
app = Dash()

app.layout = [
    html.Div(children='Yahoo finance data from 2025-01-01 to 2025-03-06'),
    #dcc.Graph(figure=px.line([0,1], title='BTC-USD'), id='my-graph')
    dcc.Graph(figure=fig, id='btc-graph'),
    html.Div([
            dcc.Markdown("""
                **Zoom and Relayout Data**

                Click and drag on the graph to zoom or click on the zoom
                buttons in the graph's menu bar.
                Clicking on legend items will also fire
                this event.
            """),
            html.Pre(id='relayout-data', style=styles['pre']),
        ], className='three columns')
]

# @app.callback(
#     Output('hover-data', 'children'),
#     Input('basic-interactions', 'hoverData'))
# def display_hover_data(hoverData):
#     return json.dumps(hoverData, indent=2)
#
#
# @app.callback(
#     Output('click-data', 'children'),
#     Input('basic-interactions', 'clickData'))
# def display_click_data(clickData):
#     return json.dumps(clickData, indent=2)


@app.callback(
    Output('relayout-data', 'children'),
    Input('basic-interactions', 'relayoutData'))
def display_relayout_data(relayoutData):
    return json.dumps(relayoutData, indent=2)

# Run the app
if __name__ == '__main__':
    #print(list(itertools.chain(*generate_plot().Close.values)))
    #print(generate_plot().index)
    app.run(debug=True, host='0.0.0.0', port=1234)
