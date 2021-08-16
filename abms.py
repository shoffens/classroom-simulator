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
start_time = time.time()  # tracks execution time

KANOTYPES = ['basic', 'satisfier', 'delighter']

DIRECTIONS = ["higher is better", "lower is better"]

# bootstrap style sheet
app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])

# ---------------


class Consumer:
    def __init__(self, stdevs, weights, kanotypes, direction):
        self.setPreferences(stdevs, weights)
        self.bestProducer = 0
        self.kanotypes = kanotypes
        self.direction = direction

    def setPreferences(self, stdevs, weights):  # creates consumer preferences
        self.preferences = []
        for stdev, weight in zip(stdevs, weights):
            weightedPreference = np.random.lognormal(
                sigma=stdev, mean=1) * weight # weighted preference with degree of randomness
            self.preferences.append(weightedPreference)

    def pickTopProduct(self, products):
        # TODO: add correct kano formulas, determine if attributes/preferences var needed
        def calculateUtilityScore(attribute, preference, kanotype, direction):
            attribute = float(attribute)
            score = 0
            
            if direction == "lower is better":
                                # make second column for reversed
                if kanotype == 'basic':
                    score = preference * (0 - math.e ** (2 * attribute - 1))
                elif kanotype == 'satisfier':
                    score = -preference * attribute
                elif kanotype == 'delighter':
                    score = preference * math.e ** (-2 * attribute - 1)
            else:
                if kanotype == 'basic':
                    score = preference * (0 - math.e ** (-2 * attribute - 1))
                elif kanotype == 'satisfier':
                    score = preference * attribute
                elif kanotype == 'delighter':
                    score = preference * math.e ** (2 * attribute - 1)

            return score

        result = {}
        for idx, product in enumerate(products): # splitting the 1st value to idx, 2nd to product
            sum = 0
            # print(f"calculating product {idx} for consumer")
            for attribute, preference, kanotype, direction in zip(product.valueList, self.preferences, self.kanotypes, self.direction): # loop through all at same time in parallel
                sum += calculateUtilityScore(attribute, preference, kanotype, direction)  # figures out score based on kanotype
            result[idx] = sum # once the score is found, consumer gets list of all products and how they are scored
        chosenIdx = max(result, key=result.get) # consumer choice of product that has best score
        products[chosenIdx].buy() # consumers buy product
        self.bestProducer = chosenIdx


class Product:
    def __init__(self, valueList, name):
        self.name = name
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.sales = 0  # The total amount of products that have been sold
        self.price = 0  # The price of the product
        self.productioncost = 0
        self.valueList = valueList

    def buy(self):
        self.sales += 1


class Attribute:
    def __init__(self, name, kano, direction, stdev, weight):
        self.name = name
        self.kanotype = kano
        self.direction = direction
        self.stdev = stdev
        self.weight = weight

    def setkanotype(self, type):
        self.kanotype = type


class Simulation:
    def __init__(self, table, consumers, days, cost, daysPerTick):
        self.df = table
        self.consumers = consumers  # number of consumers
        self.days = days  # number of days in simulation
        self.cost = cost
        # TODO: should profit be adjusted for days per tick? this skips days and chances to buy
        self.daysPerTick = daysPerTick
        self.ticks = days//daysPerTick # prevents non integer days

        self.profitPerSale = int(self.df.iloc[0, 5]) - self.cost # profit calculation

        self.attributeDF = self.df.iloc[:, 0:5] # splits data table into attributes dataframe

        self.productDF = self.df.iloc[:, 5:] # splits data table into product dataframe

        self.setAttributes() # set attributes
        self.setProducts() # set producers

        self.profitDF = {'Time (Days)': [], 'Profit ($)': []} # dict with time and profit for graphing

        for i in range(self.ticks): # loop that runs every tick
            self.consumers = [Consumer(
                self.df['Stdev'], self.df['Weight'], self.df['Kanotype'], self.df['Direction']) for _ in range(consumers)] # for amount of customers specified

            for consumer in self.consumers:
                consumer.pickTopProduct(self.products) # for every consumer in the list, calls pickTopProduct with list of products in the simulation
            self.profitDF['Time (Days)'].append(i*self.daysPerTick) # sets day for x axis on graph
            self.profitDF['Profit ($)'].append( 
                self.products[0].sales * self.profitPerSale) # sets profit for y axis

    def setAttributes(self):
        attributes = []
        for _, row in self.attributeDF.iterrows():
            attribute = None
            if not None in row.values:
                attribute = Attribute(*row.values)
            attributes.append(attribute)
        self.attributes = attributes

    def setProducts(self):
        products = []
        for col in self.productDF:
            values = self.productDF[col]
            products.append(Product(values.values, col))
        self.products = products

    def getProfitData(self):
        return self.profitDF

    def getMarketShares(self):
        ms = {'Product Name': [], 'Sales': []}
        for product in self.products:
            ms['Product Name'].append(product.name)
            ms['Sales'].append(product.sales)
        df = pd.DataFrame(ms)
        return df

    # def generate_df(self): # generates dataframe
    #  TODO: do appropriate calculations and return market share and profit dataframes, or one that is later sliced

# -------------------------------------------------------


controls = dbc.Card(  # apply button -- not needed?
    [
        dbc.Button('Apply', id='submit-button', color='primary',
                   block=True, className='mr-1')
    ],
    body=True,
)

# -----------    page layout   ------------------------


app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1("ABM Market Simulator"),
                    style={"textAlign": "center"})),
    dbc.Row(dbc.Col(html.P("Welcome to the ABM Market Simulator, where you will simulate your product in the market."),
                    style={"textAlign":"center", "marginLeft": "75px","marginRight":"75px"})),
    dbc.Row(dbc.Col(html.P("You will assume the role of the producer developing a new product, and will enter information about the product and its competitors. Consumers will then choose which products to purchase, revealing trends in market share and your new product's profits."),
                    style={"textAlign":"center", "marginLeft": "75px","marginRight":"75px"})),
    dbc.Row(dbc.Col(html.P("Add or remove products and attributes by pressing the associated buttons. Rename products by pressing the pencil icon in the cell's header. Click on each cell or tab between them to input information. Score STdev, Weight, and all product scores between 1 and 10. Consumer count and the number of days to simulate will determine the sales in your simulation - aim for 3-5 years (~1000-1800 days). Enter the cost to produce your new product to determine your profits. Press the ""Run Simulation"" button to update the outputs. To analyze the graphs, hover over each to determine an exact number of sales or profits. Drag the cursor over segments of the profit graph to look at a section in greater detail. If the page fails to load at any point, press the ""Run Simulation"" button again; if that fails, refresh the page and reenter the information."),
                    style={"textAlign":"center", "marginLeft": "75px","marginRight":"75px"})),
    dbc.Row([
            dbc.Col(children=html.Div([

                dbc.Form([
                    dbc.Input(
                        id='adding-rows-name',
                        placeholder='Enter a product name...',
                        value='',
                        style={'width': '250px'},
                        className="mx-2"
                    ),
                    dbc.Button('Add Product',
                               id='add-column-button', n_clicks=0, className="mr-4"),

                ], inline=True, className='my-2'),

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

                        {'name': 'Direction', # higher/lower is better
                         'id': 'Direction',
                         'presentation': 'dropdown',
                         'deletable': False,
                         'renamable': False},

                        {'name': 'Stdev',
                         'id': 'Stdev',
                         'deletable': False,
                         'renamable': False,
                         'type': 'numeric'},

                        {'name': 'Weight',
                         'id': 'Weight',
                         'deletable': False,
                         'renamable': False,
                         'type': 'numeric'},

                        {'name': 'New Product',
                         'id': 'NewProduct',
                         'deletable': False,
                         'renamable': False,
                         'type': 'numeric'},

                        {'name': 'Competitor 1',
                         'id': 'Competitor-1',
                         'deletable': False,
                         'renamable': True,
                         'type': 'numeric'},
                    ],

                    dropdown={
                        'Kanotype': {
                            'options': [
                                {'label': i, 'value': i}
                                for i in KANOTYPES
                            ]
                        },
                        'Direction': {
                            'options': [
                                {'label': i, 'value': i}
                                for i in DIRECTIONS
                            ]
                        }

                        
                        },

                    data=[
                        {
                            'Attribute': 'Price',
                            'Kanotype': 'satisfier',
                            'Direction': 'lower is better',
                            'Stdev': None,
                            'Weight': None,
                            'NewProduct': None,
                            'Competitor-1': None
                        }]+[
                        {
                            'Attribute': None,
                            'Kanotype': None,
                            'Direction': 'higher is better',
                            'Stdev': None,
                            'Weight': None,
                            'NewProduct': None,
                            'Competitor-1': None
                        }
                        for i in range(1)
                    ],
                    editable=True,
                    row_deletable=True,

                    style_header={
                    'backgroundColor': 'rgb(126, 182, 196)',
                    'color':'darkslategrey',
                    'fontWeight': 'bold'
                    },

                    style_cell={
                    'textAlign': 'right',
                    'color':'darkslategrey'},

                    css=[{"selector": ".Select-menu-outer",
                          "rule": "display: block !important"}],
                    

                ),
                

                dbc.Form(
                    [
                        dbc.Button('Add Attribute', id='add-row-button',
                                   n_clicks=0, className="mx-3"),
                        dbc.FormGroup(
                            [
                                # TODO: add html_for tags to the labels to link them with inputs
                                dbc.Label("Consumers", className="mr-2"),
                                dbc.Input(
                                    id='consumers-in-market', placeholder='Enter # of consumers', type='number'),
                            ],
                            className="mr-3",
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Days", className="mr-2"),
                                dbc.Input(id='days', placeholder='Enter days',
                                          type='number'),
                            ],
                            className="mr-3",
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Days/Tick", className="mr-2"),
                                dbc.Input(
                                    id='daysPerTick', placeholder='Enter days per tick', type='number'),
                            ],
                            className="mr-3",
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Cost", className="mr-2"),
                                dbc.Input(
                                    id='production-cost', placeholder='Enter production cost', type='number'),
                            ],
                            className="mr-5",
                        ),
                        
                        dbc.Button('Run Simulation',
                                   id='run-sim', color="success"),
                    ],
                    inline=True, className='my-2'),
            ]),

                width=12, style={'backgroundColor': 'rgb(45, 101, 115)'}),


            dbc.Col(html.Div(dcc.Graph(id='pie-chart')), width=6),
            dbc.Col(html.Div(dcc.Graph(id='line-graph')), width=6),
            ])
])


# ------------------ end of layout --------------------

@app.callback(  # adds attributes
    Output('adding-rows-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns}) # TODO: should this set the cells equal to None?
    return rows


prevent_initial_call = True


@app.callback(  # adds products
    Output('adding-rows-table', 'columns'),
    Input('add-column-button', 'n_clicks'),
    State('adding-rows-name', 'value'),
    State('adding-rows-table', 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        if not value:
            value = f"Competitor {n_clicks+1}"
        existing_columns.append({
            'id': value, 'name': value, 'editable': True,
            'renamable': True, 'deletable': True
        })
    return existing_columns


prevent_initial_call = True


@app.callback(
    Output('pie-chart', 'figure'),
    Output('line-graph', 'figure'),
    Input('run-sim', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('consumers-in-market', 'value'),
    State('production-cost', 'value'),
    State('days', 'value'),
    State('daysPerTick', 'value'))
def generate_chart(n_clicks, table, consumers, cost, days, daysPerTick):
    if n_clicks is None:
        raise PreventUpdate
    else:
        df = pd.DataFrame.from_records(table)

        sim = Simulation(df, consumers, int(days), cost, daysPerTick)

        ms = sim.getMarketShares()
        pie = px.pie(ms, values='Sales', names='Product Name',hover_name='Product Name', title='Market Share', color_discrete_sequence=px.colors.qualitative.Prism, ) # pie chart: market share

        profit = sim.getProfitData()
        line = px.line(profit, x="Time (Days)", y="Profit ($)", title='New Product Cumulative Profit', color_discrete_sequence=px.colors.qualitative.Prism) # line graph: profit
        return pie, line,


prevent_initial_call = True


# -------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
