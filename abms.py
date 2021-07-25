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
        for stdev, weight in zip(stdevs, weight):
            weightedPreference = np.random.normal(scale=stdev) * weight
            self.preferences.append(weightedPreference)

    def pickTopProduct(self, products):
        def calculateUtilityScore(attributes, preference, kanotype):
            score = 0
            if kanotype == 'basic':
                score = preference * (0 - math.e ** (-2 * attribute - 1))
            elif kanotype == 'satisfier':
                score = preference * attribute
            elif kanotype == 'delighter':
                score = preference * math.e ** (2 * attribute - 1)
            elif kanotype == 'basic (reversed)':
                score = preference * (0 - math.e ** (2 * attribute - 1))
            elif kanotype == 'satisfier (reversed)':
                score = -preference * attribute
            elif kanotype == 'delighter (reversed)':
                score = preference * math.e ** (-2 * attribute - 1)
            return score

        result = {}
        for idx, product in enumerate(products):
            sum = 0
            for attribute, preference, kanotype in zip(product.valueList, self.preferences, self.kanotypes):
                sum += calculateUtilityScore(attribute, preference, kanotype)
            result[idx] = sum
        chosenIdx = max(result, key=result.get)
        products[chosenIdx].buy()
        self.bestProducer = chosenIdx

class Producer:
    def __init__(self, name, valueList):
        self.name = name
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.sales = 0 # the total amount of products that have been sold
        self.price = 0 # the price of the product
        self.productioncost = 0 # cost of producing item
        self.valueList = valueList # list of attribute scores

    def buy(self): # determines if sale is made, product is bought
        self.sales += 1

class Attribute:
    def __init__ (self, name, kanotype, stdev, weight):
        self.name = name
        self.kanotype = kanotype
        self.stdev = stdev
        self.weight = weight

    def setkanotype(self,type):
        self.kanotype = type


class Simulation: # components of simulation, data table + buttons
    def __init__ (self, table, consumers, days, cost, daysPerTick):
        self.df = table
        self.consumers = consumers # number of consumers ("buyers")
        self.days = days # number of days in simulation
        self.cost = cost # production cost
        self.daysPerTick = daysPerTick # days per tick in simulation
        self.ticks = days//daysPerTick # returns days integer values
    
        self.profitPerSale = int(self.df.iloc[0, 4]) - self.cost

        self.attributeDF = self.df.iloc[:, 0:4]

        self.productDF = self.df.iloc[:, 4:]

        self.setAttributes(self.attributeDF)
        self.setProducts(self.productDF)

        self.profitDF = {'time': [], 'profit': [] } 

        for i in range(self.ticks):
            self.consumers = [Consumer(self.df['Stdev'], self.df['Weight'], self.df['Kanotype']) for _ in range(consumers)]

            
            for consumer in self.consumers:
                consumer.pickTopProduct(self.products)
            # max_obj = max(self.products, key=lambda p: p.sales)
            self.profitDF['time'].append(i*self.daysPerTick)
            self.profitDF['profit'].append(self.products[0].sales * self.profitPerSale)
        
    def setAttributes(self, attributeDF):
        attributes = []
        for _, row in self.attributeDF.iterrows():
            attribute = None
            if not None in row.values:
                attribute = Attribute(*row.values)
            attributes.append(attribute)
        self.attributes = attributes
    
    def setProducts(self, Product, productDF):
        products = []
        for col in productDF:
            values = productDF[col]
            products.append(Product(values.values, col))
        self.products = products


    def getProfitData(self):
        return self.profitDF
    
    
    def getMarketShares(self):
        ms = {'name': [], 'sales': [] } # TODO: optimize
        for product in self.products:
            ms['name'].append(product.name)
            ms['sales'].append(product.sales)
        df = pd.DataFrame(ms)
        return df

    # def generate_df(self): # generates dataframe
    #  TODO: do appropriate calculations and return market share and profit dataframes, or one that is later sliced

# -------------------------------------------------------

controls = dbc.Card( # apply button
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
             'renamable': False,
             'type':'numeric'},

            {'name': 'New Product',
             'id': 'NewProduct',
             'deletable': False,
             'renamable': False,
             'type':'numeric'},

            {'name': 'Competitor 1',
             'id': 'Competitor-1',
             'deletable': False,
             'renamable': True,
             'type':'numeric'},             
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
                'Attribute': 'Price',
                'Kanotype': 'satisfier (reversed)', 
                'Stdev': None,
                'Weight': None,
                'New Product': None,
                'Competitor-1': None
            }
            for i in range(1)
        ],
        editable=True,
        row_deletable=True,

        css=[{"selector": ".Select-menu-outer", "rule": "display: block !important"}],

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
        dbc.Col(dbc.Input(id='consumers-in-market', placeholder='Consumers in market', type='number'), width=2),
        dbc.Col(dbc.Input(id='days', placeholder='Days to simulate', type='number'), width=2),
        dbc.Col(dbc.Input(id='daysPerTick', placeholder='Days Per Tick', type='number'), width=2),
        dbc.Col(dbc.Input(id='production-cost', placeholder='Production cost of new product', type='number'), width=3),
        dbc.Col(dbc.Button('Run Simulation', id='run-sim'), width=2)
        ], justify="start")
]),

width=12,style={'background-color': 'rgb(45, 101, 115)'}),


dbc.Col(html.Div(dcc.Graph(id='line-graph')), width=6),
dbc.Col(html.Div(dcc.Graph(id='pie-chart')), width=6), # fix to make it pie chart
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

@app.callback( # pie chart: market share
    Output('pie-chart', 'figure'), 
    Output('line-graph', 'figure'),
    Input('run-sim', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('consumers-in-market', 'value'),
    State('production-cost', 'value'),
    State('days', 'value'),
    State('daysPerTick','value'))
def generate_chart(n_clicks, table, consumers, cost, days, daysPerTick): 
    if n_clicks is None:
        raise PreventUpdate
    else:
        df = pd.DataFrame.from_records(table)
        sim = Simulation(df, consumers, int(days), cost, daysPerTick)

        ms = sim.getMarketShares()
        pie = px.pie(ms, values='sales', names='names')

        profit = sim.getProfitData()
        line = px.line(profit, x='time', y='profit')
        return pie, line


# -------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)