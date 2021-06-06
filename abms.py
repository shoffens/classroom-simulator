import pandas as pd
import math
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output 
import plotly.express as px
from statistics import mean
import time
start_time = time.time() # tracks execution time

app = dash.Dash(external_stylesheets=[dbc.themes.YETI]) # bootstrap style sheet

##

class Consumer:
    def __init__(self, attributes,productLifespans):
        self.preferences = attributes # Randomly generated, based on normal distributions; used in utility function
        self.bestProducer = 0 # Initially, all consumers are considered to be consumers of product 0
        self.productLifespan = -1 # A lifespan of less than 0 means the consumer no longer owns a product, initializes
        self.productLifespans = productLifespans # list of all lifespans for products (user input)
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.consumerCount = 0 # number of consumers in simulation, representing larger population
        self.buyers = 0 # number of total population
        self.consumerScale = 0 # The number of actual consumers represented by 1 consumer in the simulation
        self.days = 0 # number of days in simulation

    def setconsumerScale(self, buyers, consumerCount):
        self.consumerScale = (buyers / consumerCount) # Define number of real-world consumers represented by each consumer in the model

    def setdays(self):
        self.days = 1 # Avoids calculation errors in first tick when days=0

    def setProductLifespan(self):
        self.productLifespan = max(self.productLifespans) * 2.5 * 365

# 

class Producer:
    def __init__(self, avgProductLifespans):
        self.avgProductLifespan = -1 # product-lifespan; The average amount of time (in years) before the product breaks
        self.avgProductLifespans = avgProductLifespans
        self.sales = 0 # The total amount of products that have been sold
        self.price = 0 # The price of the product

#

class CustomerPreferences:
    def __init__(self, kanotypes, spread, weight):
        self.productAttributes # A list of attribute values for this producer's product (user input)
        self.kanotypes = kanotypes
        self.spread = spread
        self.weight = weight

#

class ProductAttributes:
    def __init__(self):
        self.productvalues = 0
        self.productlife = 0
        self.productioncost = 0

# # attribute class
# class Attribute:
#     def __init__(self, name, stddev, weight, kanotypes, productvalues):
#         self.name = name
#         self.preference = np.random.normal(0, stddev, 1) * weight # creates preferences for consumer, based on stddev and mean of 1, multipled by weight
        # self.kanotypes = kanotypes
#         self.productvalues = productvalues


# ----------------------------------------------------

# functions to transfer

# 1. max lifespan - DONE for now
# 2. normalize attributes
# 3. kano types
# 4. consumer preferences - DONE for now
# 5. number of real world consumers - DONE for now
# 6. day ticks - DONE for now


# -----------------------------------------------------------------------------------------------------


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
            dbc.Row([dbc.Col(html.Div(name)), dbc.Col(dcc.Input(id=f"input{attrNum}", type="text", placeholder=f"input{attrNum}"))]),
            # dbc.Row(
                # [
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

app.layout = html.Div([
    
dbc.Card(
    dbc.CardBody([
        dbc.Col([
            dbc.Col([ # title text
                titletext()
            ], width=12, align='center'),

            html.Br(),

dbc.Col([                
    dbc.Card([
        dbc.Col([ # 1st attribute card
            attributeCard("Attribute 1", 1),
        

        html.Br(),

        ], width='15', align='center'),

        dbc.Col([
            attributeCard("Attribute 2", 2) # 2nd attribute card
        ], width='15', align='center'),

        html.Br(),

        dbc.Col([
            attributeCard("Attribute 3", 3)
        ], width='15',align='center'),

        html.Br(),

        dbc.Col([
            attributeCard("Attribute 4", 4)
        ], width='15',align='center'),

        html.Br(),

        dbc.Col([
            attributeCard("Attribute 5", 5) # 5th attribute card
        ], width='15',align='center'),

        html.Br(),

        dbc.Card(
        [
            dbc.Button('Apply', id='submit-button', color='secondary')
            ],
            
        )])], width='2', align='left')
        
        
    ], align='left'),
    html.Br(),

        ]), color = 'dark'
    )
])

# -------------------------------------------------------

# run

if __name__ == '__main__':
    app.run_server(debug=True)