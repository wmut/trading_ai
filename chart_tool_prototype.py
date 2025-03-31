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
    btc_data = yf.download(ticker, start='2025-01-01', end='2025-03-06', interval='1h')

    # prepare dataframe of long format
    df = btc_data["Close"]
    df["date"] = btc_data.index
    print(df.head())

    return df


def create_ticker_chart(df, ticker):
    # Some plotly magic
    fig = px.line(df, x="date", y=ticker, title=ticker)

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

    return fig

df1 = create_ticker_data('tab-0', 'BTC-USD')
df2 = create_ticker_data('tab-1', 'XRP-USD')

# App Layout
css = ["https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", ]
app = Dash(name="AI Trading Dashboard", external_stylesheets=css)

#dcc.Graph(figure=px.line([0,1], title='BTC-USD'), id='my-graph')
#html.Div([dashboard,
#html.Div(
#dcc.Input(id='AgentID', type='text')),
#html.Button('Submit', id='button'),
# dcc.Tabs(id='tabs-example', value='tab-1-example',
# children=[
# dcc.Tab(label='Tab1', value='tab-1'),
# dcc.Tab(label='Tab2', value='tab-2')
# ]),#],html.Div(id='output-tab')),

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
        dcc.Tab([html.Div(children='Yahoo finance data from 2025-01-01 to 2025-03-06'),
            dcc.Graph(figure=create_ticker_chart(df1, 'BTC-USD'), id='btc-graph'),
            html.Div([
                    dcc.Markdown("""
                        **Zoom and Relayout Data**

                        Click and drag on the graph to zoom or click on the zoom
                        buttons in the graph's menu bar.
                        Clicking on legend items will also fire
                        this event.
                    """),
                    html.Pre(id='relayout-data', style=styles['pre']),
                ], className='three columns')], label="BTC"),
        dcc.Tab([html.Br(),
            html.Div(children='Yahoo finance data from 2025-01-01 to 2025-03-06'),
            dcc.Graph(figure=create_ticker_chart(df2, 'XRP-USD'), id='btc-graph'),
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
    #print(list(itertools.chain(*generate_plot().Close.values)))
    #print(generate_plot().index)
    app.run(debug=True, host='0.0.0.0', port=1234)
