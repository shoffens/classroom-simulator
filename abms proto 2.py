import pandas as pd
import math
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
from collections import deque
from statistics import mean
import time
start_time = time.time() # tracks execution time

app = dash.Dash(external_stylesheets=[dbc.themes.YETI]) # bootstrap style sheet

##

consumerAttributes = {
    'spread': range(0,1), 
    'weight': [1,2,3,4,5,6,7,8,9,10],
    'kanotypes':['basic','satisfier','delighter']
    }

consumerCount = 0 # number of consumers in simulation, representing larger population
buyers = 0 # number of total population outside of simulation
consumerScale = 0 # The number of actual consumers represented by 1 consumer in the simulation
days = 1 # number of days in simulation
currentmonth = (days * 12 / 365)
currentyear = (days / 365)

#consumerScale = (buyers / consumerCount) # Define number of real-world consumers represented by each consumer in the model

##

class Consumer:
    def __init__(self, attributes,productLifespans, days=1):
        self.preferences = attributes # Randomly generated, based on normal distributions; used in utility function
        self.bestProducer = 0 # Initially, all consumers are considered to be consumers of product 0
        self.productLifespan = -1 # A lifespan of less than 0 means the consumer no longer owns a product, initializes
        
    def setpreferences(self, weight): 
        self.preferences = np.random.normal(scale=1) * weight # creates preferences for consumer, based on stddev of 0-1, multipled by weight

    def setProductLifespan(self):
        self.productLifespan = max(self.productLifespans) * 2.5 * 12 # 2.5 sets it to be a 10x multiplier for the inputted product lifespan
  

# 

class Producer:
    def __init__(self, avgProductLifespan, productLifespans):
        self.avgProductLifespan = -1 # product-lifespan; The average amount of time (in years) before the product breaks
        self.productLifespans = productLifespans # list of all lifespans for products (user input)
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.sales = 0 # The total amount of products that have been sold
        self.price = 0 # The price of the product
        self.productvalues = 0
        self.productlife = 0
        self.productioncost = 0
        self.productAttributes # A list of attribute values for this producer's product (user input)
        

    def setavgProductLifespan(self, average):
        self.avgProductLifespan = average(self.avgProductLifespan) * 365

##

# defining functions for layout


# text field and titles
def titletext():
    return html.Div([ 
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2("Market Simulator"),
                    html.P("Interactively simulate market conditions")
                ], style={'textAlign': 'center'})
            ])
        ),
    ])


# slider function for weight and standard dev
def slider(name, id, min, max, step):
    return html.Div(
            [
                dbc.Label(name),
                html.Br(),
                html.Div(
                    [dcc.Slider(
                    id=id, min=min, max=max, step=step, 
                    value=0.1, tooltip={'always_visible': True, 'placement': 'bottom'})
                    ],)
                
        ]
    )


# attribute card function that takes in the attribute name and number
# returns attribute info, weight, standard dev slider into one card
def attributeCard(name, attrNum):
    return dbc.Card(
        [
            dbc.Row([dbc.Col(html.Div(name)), dbc.Col(dcc.Input(id=f"input {attrNum}", type="text", placeholder=f"input {attrNum}"))]),
            # dbc.Row(
                # [
                    html.Div(
                        id='output'),
                    html.Div(
                        slider("Weight", f"Weight {attrNum}", 1, 10, 1),
                        ), 
                        slider("Standard Deviation", f"Standard Deviation {attrNum}", 0, 1, .05),

                # ])
        ])


# -------------------------------------------------------

controls = dbc.Card( # defines controls, does not put them on screen
    [
    dbc.Button('Apply', id='submit-button', color='primary', block=True)
    ],
    body=True,
)

# -----------------------------------------------------

# page layout

X = deque(maxlen=20)
X.append(1)
Y = deque(maxlen=20)
Y.append(1)


app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1*1000
        ),
    ]
)

@app.callback(Output('live-graph', 'figure'),
              events=[Input('graph-update', 'interval')])
def update_graph_scatter():
    X.append(X[-1]+1)
    Y.append(Y[-1]+Y[-1]*random.uniform(-0.1,0.1))

    data = plotly.graph_objs.Scatter(
            x=list(X),
            y=list(Y),
            name='Scatter',
            mode= 'lines+markers'
            )

    return {'data': [data],'layout' : go.Layout(xaxis=dict(range=[min(X),max(X)]),
                                                yaxis=dict(range=[min(Y),max(Y)]),)}




# run

if __name__ == '__main__':
    app.run_server(debug=True)