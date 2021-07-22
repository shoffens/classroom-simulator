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
start_time = time.time() # tracks execution time

KANOTYPES = ['basic', 'satisfier', 'delighter']

app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR]) # bootstrap style sheet

# ---------------

class Consumer:
    def __init__(self, attributes):
        self.preferences = attributes # Randomly generated, based on normal distributions; used in utility function
        self.bestProducer = 0 # Initially, all consumers are considered to be consumers of product 0
        
    def setpreferences(self, weight): 
        self.preferences = np.random.normal(scale=1) * weight # creates preferences for consumer, based on stddev of 0-1, multipled by weight


class Producer:
    def __init__(self):
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.sales = 0 # The total amount of products that have been sold
        self.price = 0 # The price of the product
        self.productvalues = 0
        self.productlife = 0
        self.productioncost = 0

    class ProductAttributes:
        def __init__ (self):
            self.spread = range(0,1)
            self.weight = [1,2,3,4,5,6,7,8,9,10]
            self.kanotype

        def setkanotype(self,type):
            self.kanotype = type

        def calculateUtilityScore(self, preferences):
            score = 0
            if self.kanotype == 'basic':
                score = preferences * (0 - math.e ^ (2 * preferences - 1))
                return score
                # preferences * (0 - e ^ (2 * attributes - 1))
            if self.kanotype == 'satisfier':
                score = preferences
                return score
                # preferences * attributes
            if self.kanotype == 'delighter':
                score = preferences * math.e ^ 2 * preferences - 1
                return score
                # preferences * e ^ 2 * attributes - 1

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
        self.consumerCount = 0 # number of consumers in simulation, representing larger population
        self.buyers = 0 # number of total population outside of simulation
        self.consumerScale = 0 # The number of actual consumers represented by 1 consumer in the simulation
        self.days = 1 # number of days in simulation
        self.currentmonth = (days * 12 / 365)
        self.currentyear = (days / 365)
        self.ticks = 1 # set to 1 to produce count of days
        self.daysPerTick = 0 # start at 0 so ticks will count from day 1

    def setconsumerScale(self,buyers,consumerCount): # Defines number of real world consumers represented
        self.consumerScale = (buyers / consumerCount)
       
    def setdays(self,ticks,daysPerTick): # Update the amount of days that have elapsed
        self.days = ticks * (daysPerTick + 1)
        return ticks # update the simulation graphs to current day  ----------------------- UPDATE once plots are made

    
    
    # def setconsumerScale(self,buyers,consumerCount): # Defines number of real world consumers represented
    #     self.consumerScale = (buyers / consumerCount)
       
    # def setdays(self,ticks,daysPerTick): # Update the amount of days that have elapsed
    #     self.days = ticks * (daysPerTick + 1)
    #     return ticks # update the simulation graphs to current day  ----------------------- UPDATE once plots are made

    
    
    # def generate_df(self): # generates dataframe
    #  TODO: do appropriate calculations and return market share and profit dataframes, or one that is later sliced
    #     created_dict = {'col': user_input, 'value': user_input * 3}
    #     df = pd.DataFrame(created_dict)
    #     return df

    #     ;; Reports the yearly profit of a producer
    # to-report daily-profit-of-producer [ producer-number ]
    #   report (([sales] of producer producer-number) * ([price] of producer producer-number) * consumer-scale / days)
    # end

    # ;; Reports the yearly profit of a producer
    # to-report monthly-profit-of-new-product
    #   report ([sales] of producer 0 * (p1-att-1 - p1-cost) * consumer-scale) / (current-month)
    # end

    # ;; Reports the current year of the simulation
    # to-report current-year
    #   report (days / 365)
    # end

    # ;; Reports the current month of the simulation
    # to-report current-month
    #   report (days * 12 / 365)
    # end


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
        id='adding-rows-table',
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
        # columns=[{
        #     'name': 'Column {}'.format(i),
        #     'id': 'column-{}'.format(i),
        #     'deletable': True,
        #     'renamable': True
        # } for i in range(1, 5)],


        data=[
            {
                'Attribute': None,
                'Kanotype': None,
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

# TODO: put elements in one horizontal row and fix their formatting
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
    return existing_columns # need to find a way to add multiple column names; overrides name


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
# @app.callback(
#     [Output('square', 'children'),
#      Output('cube', 'children'),
#      Output('twos', 'children'),
#      Output('threes', 'children'),
#      Output('x^x', 'children')],
#     [Input('x1', 'value'),
#      Input('y1', 'value'),
#      Input('x2', 'value'),
#      Input('y2', 'value'),
#      Input('y3', 'value')])
# def update_graph(x1, y1, x2, y2, y3):
#     return x1**2, y1**3, x2**x2, y2**y2, y3**y3

    # Output("pie-chart", "figure"),  # pie chart
    # (Output('memory', 'data'), # updates dcc.store to have generated data
    # (Output('queryTable', 'data') # fetches data from storage to show plots

    # [Input("names", "value"), # pie chart
    # Input("values", "value")]) # pie chart
    # [Input('button', 'n_clicks')]) # dcc.store
    # [Input('memory', 'data')]) # storage data from dcc.store


# def generate_chart(names, values):
#     fig = px.pie(df, values=values, names=names)
#     return fig


# run

if __name__ == '__main__':
    app.run_server(debug=True)