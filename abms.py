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

app = dash.Dash(external_stylesheets=[dbc.themes.SLATE])

##

# class Consumer:
#     def __init__(self, preferences, bestProducer, productLifespan, profit):
#         # function inside is called a method. double underscore is a dunder. it is special.
#         # init describes what happens when you create a version of the class. it takes arguments

#         self.preferences = []
#         self.bestProducer = 
#         self.productLifespan
#         self.profit
#         # preferences       ; Randomly generated, based on normal distributions; used in utility function
#         # best-producer     ; The producer that this consumer last purchased a product from
#         # product-lifespan  ; The current lifespan of the product
#         # profit            ; Total profit accumulated

# class Attribute:
#     def __init__(self, stddev, weight):
#         self.preference = np.random.normal(0, stddev, 1) * weight

##


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

##

controls = dbc.Card( # defines controls, does not put them on screen
    [

        dbc.FormGroup(
            [
                dbc.Label('Standard Deviation'),
                html.Br(),
                dcc.Slider(
                    id='standard deviation', min=0.00, max=1.00, step=0.05, 
                    value=0.1, tooltip={'always_visible': True, 'placement': 'bottom'}
            ),
        ]
    ),
    dbc.FormGroup(
        [ 
            dbc.Label('Weight'),
            html.Br(),
            dcc.Slider(
                id='weight', min=1, max=5, step=1, value=3,
                tooltip={'always_visible': True, 'placement': 'bottom'}
            ),
        ]
    ),

    dbc.Button('Apply', id='submit-button', color='primary', block=True)
    ],
    body=True,
)

# making rows
# def attributerow(name):
#     return html.Div(
#         dbc.Row(dbc.Col(html.Div(name),
#             dbc.Row(
#                 [ 
#                     dbc.Col(html.Div("Weight")),
#                     dbc.Col(html.Div('Standard Deviation')),
#                 ]
#             )))

def slider(name, id, min, max, step):
    return html.Div(
            [
                dbc.Label(name),
                html.Br(),
                dcc.Slider(
                    id=id, min=min, max=max, step=step, 
                    value=0.1, tooltip={'always_visible': True, 'placement': 'bottom'}
            ),
        ]
    )

def attributeCard(name, attrNum):
    return dbc.Card(
        [
            dbc.Row([dbc.Col(html.Div(name)), dbc.Col(dcc.Input(id=f"input{attrNum}", type="text", placeholder=f"input{attrNum}"))]),
            dbc.Row(
                [
                    dbc.Col(html.Div(slider("Weight", f"Weight {attrNum}", 1, 5, 1))),
                    dbc.Col(html.Div(slider("Standard Deviation", f"Standard Deviation {attrNum}", 0, 1, .05))),

                ]
            ),
        ]
    )


#

# layout for the buttons

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Col([
                dbc.Col([
                    titletext()
                ], width=12, align='center'),
                html.Br(),

                dbc.Col([
                    attributeCard("Attribute 1", 1)
                ], width='3', align='center'),
                html.Br(),
                dbc.Col([
                    attributeCard("Attribute 2", 2)
                ], width='3', align='center'),
                html.Br(),
                dbc.Col([
                    attributeCard("Attribute 3", 3)
                ], width='3',align='center'),
                html.Br(),
                dbc.Col([
                    attributeCard("Attribute 4", 4)
                ], width='3',align='center'),
                html.Br(),
                dbc.Col([
                    attributeCard("Attribute 5", 5)
                ], width='3',align='center'),

            ], align='left'), 
            html.Br(),

        ]), color = 'dark'
    )
])



# # main page layout
# dbc.Row(
#         [
#             dbc.Col(controls, md=4),
#             dbc.Col(
#                 [
#                     dcc.Graph(id='profit_graph'),
#                     dcc.Graph(id='ms_hist'),
#                     dbc.Row(
#                         [
#                             dbc.Col(dcc.Graph(id='ms_pie'), md=6)
#                         ]
#                     ),
#                 ],
#                 md=9
#             ),
#         ],
#         align='top',
#         ),
#     ],
#     fluid=True,
# )

if __name__ == '__main__':
    app.run_server(debug=True)