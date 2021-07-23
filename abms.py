from types import new_class
import pandas as pd
import math
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
from statistics import mean
import time
import dash_table
from dash.exceptions import PreventUpdate
import random
start_time = time.time() # tracks execution time

KANOTYPES = ['basic', 'satisfier', 'delighter', 'basic (reversed)', 'satisfier (reversed)', 'delighter (reversed)']

app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR]) # bootstrap style sheet

# ---------------

class Consumer: # TODO: loop to create an object for every buyer (user input), as many producers = products, list of preferences for each attribute
    def __init__(self, stdevs, weights, kanotypes):
        self.setPreferences(stdevs, weights)
        self.bestProducer = 0 #TODO: determine if bestProducer needed
        self.kanotypes = kanotypes

    def setpreferences(self, weight, stdevs):
        self.preferences = []
        for stdev, weight in zip(stdevs, weights):
            weightedPreference = np.random.normal(scale=stdev) * weight
            self.preferences.append(weightedPreference)

    def pickTopProduct(self):
        def calculateUtilityScore(attributes, preference, kanotype):
            score = 0
            if kanotype == 'basic':
                score = preference * (0 - math.e ** (-2 * attribute - 1))
                # preference * (0 - e ^ (2 * attributes - 1))
            elif kanotype == 'satisfier':
                score = preference * attribute
                # preferences * attributes
            elif kanotype == 'delighter':
                score = preference * math.e ** (2 * attribute - 1)
                # preferences * e ^ 2 * attributes - 1
            elif kanotype == 'basic (reversed)':
                score = preference * (0 - math.e ** (2 * attribute - 1))
            elif kanotype == 'satisfier (reversed)':
                score = -preference * attribute
            elif kanotype == 'delighter (reversed)':
                score = preference * math.e ** (-2 * attribute - 1))
            return score

class Producer:
    def __init__(self):
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.sales = 0 # The total amount of products that have been sold
        self.price = 0 # The price of the product
        self.productioncost = 0

    class ProductAttributes:
        def __init__ (self):
            self.spread = range(0,1)
            self.weight = [1,2,3,4,5,6,7,8,9,10]
            self.kanotype

        def setkanotype(self,type):
            self.kanotype = type

       

    #     ;; UTILITY FUNCTION
    # ; Find utility for each attribute, and sum them up into temp-utility
    # (foreach ([product-attributes] of ?) preferences attribute-kano-types [ ; 1? - product attribute, ?2 - preference, ?3 - kano type
    #     if (?3 = "delighter") [
    #       set temp-utility (temp-utility + ?2 * e ^ (2 * ?1 - 1))
    #     ]
    #     if (?3 = "satisfier") [
    #       set temp-utility (temp-utility + ?2 * ?1)
    #     ]
    #     if (?3 = "basic") [
    #       set temp-utility (temp-utility + ?2 * (0 - e ^ (-2 * ?1 - 1)))
    #     ]
    #     if (?3 = "delighter (reversed)") [
    #       set temp-utility (temp-utility + ?2 * e ^ (-2 * ?1 - 1))
    #     ]
    #     if (?3 = "satisfier (reversed)") [
    #       set temp-utility (temp-utility - ?2 * ?1)
    #     ]
    #     if (?3 = "basic (reversed)") [
    #       set temp-utility (temp-utility + ?2 * (0 - e ^ (2 * ?1 - 1)))
    #     ]
    #   ])


class Simulation:
    def __init__ (self, days):
        self.buyers = 0 # number of consumers
        self.days = 1 # number of days in simulation
        self.ticks = 1 # set to 1 to produce count of days
        self.daysPerTick = 0 # start at 0 so ticks will count from day 1

    
    # def generate_df(self): # generates dataframe
    #  TODO: do appropriate calculations and return market share and profit dataframes, or one that is later sliced

# -------------------------------------------------------

controls = dbc.Card( # defines controls, does not put them on screen
    [
    dbc.Button('Apply', id='submit-button', color='primary', block=True, className='mr-1')
    ],
    body=True,
)

# -----------    page layout   ------------------------


app.layout = html.Div([ 
    dbc.Row(dbc.Col(html.H1("ABM Market Simulator"), style={"textAlign": "center"})),
    dbc.Row(
        [ 
            dbc.Col(children=html.Div([
    html.Div([
        dcc.Input(
            id='adding-rows-name',
            placeholder='Enter a product name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Product', id='add-column-button', n_clicks=0)
    ], style={'height': 50}),

    dash_table.DataTable(
        id='adding-rows-table', # TODO: make price attribute fixed, with satisfier (reversed)
        columns=[
            {'name': 'Attribute',
             'id': 'Attribute',
             'deletable': False,
             'renamable': False},

            {'name': 'Kanotype',
             'id': 'Kanotype',
             'presentation': 'dropdown',
             'deletable': False,
             'renamable': False},

            {'name': 'Stdev',
             'id': 'Stdev',
             'deletable': False,
             'renamable': False},

            {'name': 'Weight',
             'id': 'Weight',
             'deletable': False,
             'renamable': False},

            {'name': 'New Product',
             'id': 'NewProduct',
             'deletable': False,
             'renamable': False},

            {'name': 'Competitor 1',
             'id': 'Competitor-1',
             'deletable': False,
             'renamable': True},             
        ],

        dropdown={
            'Kanotype': {
                'options': [
                    {'label': i, 'value': i}
                    for i in KANOTYPES
                ]
            }},


        data=[
            {
                'Attribute': None,
                'Kanotype': None, # TODO: tooltip for hovering over kano type dropdown, shows graph/descriptors
                'Stdev': None,
                'Weight': None,
                'New Product': None,
                'Competitor-1': None
            }
            for i in range(5)
        ],
        css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],


        editable=True,
        row_deletable=True,

        # TODO: conditionally or manually format the columns that can't be deleted

        # style_data_conditional=[{
        #     'if': {'column_deletable': False},
        #     'backgroundColor': 'rgb(30, 30, 30)',
        #     'color': 'white'
        # }],
        # style_header_conditional=[{
        #     'if': {'column_deletable': False},
        #     'backgroundColor': 'rgb(30, 30, 30)',
        #     'color': 'white'
        # }],
        
),

# TODO: put elements in one horizontal row and fix formatting
    dbc.Row([
        dbc.Col(dbc.Button('Add Attribute', id='add-row-button', n_clicks=0), width=2),
        dbc.Col(dbc.Input(id='buyers-in-market', placeholder='Buyers in market', type='number'), width=2),
        dbc.Col(dbc.Input(id='days', placeholder='Days to simulate', type='number'), width=2),
        dbc.Col(dbc.Input(id='production-cost', placeholder='Production cost of new product', type='number'), width=3),
        dbc.Col(dbc.Button('Run Simulation', id='run-sim'), width=2)
        ], justify="start")
]),

width=12,style={'background-color': 'rgb(45, 101, 115)'}),


dbc.Col(html.Div(dcc.Graph(id='line-graph')), width=6),
dbc.Col(html.Div(dcc.Graph(id='pie-chart')), width=6), #TODO: figure out why this loads like a line graph. may be related to preventUpdate
])
])



# ------------------ end of layout --------------------

@app.callback( # adds attributes 
    Output('adding-rows-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback( # adds products
    Output('adding-rows-table', 'columns'),
    Input('add-column-button', 'n_clicks'),
    State('adding-rows-name', 'value'),
    State('adding-rows-table', 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value, 'editable': True,
            'renamable': True, 'deletable': True
        })
    return existing_columns


@app.callback( # line graph: monthly profits
    Output('line-graph', 'figure'),
    Input('adding-rows-table', 'data'),
    Input('adding-rows-table', 'columns'))
def display_output(rows, columns):
    return {
        'data': [{
            'type': 'line',
           # 'y': [0], # change to profit calc
            #'x': [# representing 5 years - 0-60 (months) on x axis]
        }]
    }

@app.callback( # pie chart: market share
    Output('pie-chart', 'figure'), 
    Input('run-sim', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('buyers-in-market', 'value'),
    State('production-cost', 'value'),
    State('days', 'value'))
def generate_chart(n_clicks, table, buyers, cost, days): 
    if n_clicks is None:
        raise PreventUpdate
    else:
        print(table)
        # names = list(data[0].keys()) + ['aa']
        sim = Simulation(table, buyers, int(days), cost)

        fig = px.pie(table, values='Weight', names='Attribute')
        return fig


# -------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)