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
import json as json

# Not used
def display_newtab(n_clicks):
    print(n_clicks)
    return 'tab-1'


# Charts
def create_ticker_data(tab, ticker):
    # Define the ticker symbol for Bitcoin in USD
    if tab == 'tab-0':
        ticker = 'BTC-USD'
    elif tab == 'tab-1':
        ticker = 'XRP-USD'

    # Fetch historical data starting from January 1, 2020
    df = yf.download(ticker, start='2025-01-01', end='2025-03-06', interval='1h')

    return df


#todo fetch from web2.0
def create_resistance_levels(ticker):
    for resistance_level in resistance_levels:
        fig.add_hline(y=resistance_level)


def create_ticker_chart(df, ticker):
    # Some plotly magic
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=list(itertools.chain(*df.Open.values)), high=list(itertools.chain(*df.High.values)), low=list(itertools.chain(*df.Low.values)), close=list(itertools.chain(*df.Close.values)))])

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

    menus = list([dict(type='buttons', buttons=list([dict(label='select',
                                                        method='relayout',
                                                        args=[{'dragmode':'select', }]
                                                        ),
                                                     dict(label='marker',
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

    #fig.update_traces(marker_size=20)

    if ticker == "BTC-USD":
        support_levels = [84500, 85188, 86400]
        resistance_levels = [87341, 88000, 90907]

    elif ticker == "XRP-USD":
        support_levels = [1.77, 2.05, 2.08]
        resistance_levels = [2.15, 2.20, 2.46]

    for resistance_level in resistance_levels:
        fig.add_hline(y=resistance_level, fillcolor='black', opacity = 0.9)

    for support_level in support_levels:
        fig.add_hline(y=support_level, fillcolor='black', opacity = 0.9)

    return fig

clicked = []
df1 = create_ticker_data('tab-0', 'BTC-USD')
df2 = create_ticker_data('tab-1', 'XRP-USD')

# App Layout
#css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = Dash(__name__, external_stylesheets=css)

css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", ]
app = Dash(name=__name__, external_stylesheets=css)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

app.layout = [
    html.Div([
    html.H1("Chart Dashboard", className = "text-center fw-bold m-2"),
    html.Br(),

    dcc.Tabs([
        dcc.Tab([html.Br(),
            html.Div(children='Yahoo finance data from 2025-01-01 to 2025-03-06'),
            dcc.Graph(figure=create_ticker_chart(df1, 'BTC-USD'), id='btc-graph'),
            html.Div([
                    html.Div(className='row', children=[
                        html.Div([
                            dcc.Markdown("""
                                **Click Data**

                                Click on points in the graph.
                            """),
                            html.Pre(id='click-data', style=styles['pre']),
                        ], className='three columns'),
                ])], className='three columns')], label="BTC"),
        dcc.Tab([html.Br(),
            html.Div(children='Yahoo finance data from 2025-01-01 to 2025-03-06'),
            dcc.Graph(figure=create_ticker_chart(df2, 'XRP-USD'), id='xrp-graph'),
            html.Div([
                    dcc.Markdown("""
                        **Zoom and Relayout Data**

                        Click and drag on the graph to zoom or click on the zoom
                        buttons in the graph's menu bar.
                        Clicking on legend items will also fire
                        this event.
                    """),
                    html.Pre(id='relayout-data', style=styles['pre']),
                ], className='three columns')], label="XRP")
        ])
    ], style={"background-color": "#D3D3D3"}) #"height": "100vh"
]

@app.callback(
    Output("click-data", "children"),
    Input("btc-graph", "clickData"),
)
def display_click_data(clickData):
    global clicked
    clicked.append(clickData)
    print(clicked)
    return json.dumps(clicked, indent=2)

#def click(clickData):
#    if not clickData:
#        raise dash.exceptions.PreventUpdate
#    print(clickData)
    #return json.dumps({k: clickData["points"][0][k] for k in ["x", "y"]})

#@app.callback(
#    Output('btcchart', 'figure'),
#    Input('some_variable', 'value')):
#    return redraw_some_graph(variable)

# use with drapodwn e.g.
#variable = dcc.Drapdown(id="some_variable", options=some_options, value="test_value", clearable=False)

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

# @app.callback(Output('tabs','active_tab'), Input('details_button','n_clicks'))
#
#
# @app.callback(
#     Output('relayout-data', 'children'),
#     Input('basic-interactions', 'relayoutData'))
# def display_relayout_data(relayoutData):
#     return json.dumps(relayoutData, indent=2)

#
#

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1234)
