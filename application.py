import pandas as pd
import math
import numpy as np
import dash
from dash import dcc
from dash import html
# from dash import dbc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import plotly.express as px
from statistics import mean
import time
from dash import dash_table
from dash.exceptions import PreventUpdate
start_time = time.time()  # tracks execution time

KANOTYPES = ['basic', 'satisfier', 'delighter'] # kano types

DIRECTIONS = ["higher is better", "lower is better"] # indicates reversed kano types

# bootstrap style sheet
application = dash.Dash(external_stylesheets=[dbc.themes.SOLAR])
server = application.server

# ---------------


class Consumer:
    def __init__(self, stdevs, weights, kanotypes, direction, monthsPerTick):
        self.setPreferences(stdevs, weights)
        self.bestProducer = 0
        self.kanotypes = kanotypes
        self.direction = direction
        self.ownedProductRemainingLifespan = 0
        self.monthsPerTick = monthsPerTick

    def setPreferences(self, stdevs, weights):  # creates consumer preferences
        self.preferences = []
        for stdev, weight in zip(stdevs.values, weights.values):
            weightedPreference = np.random.lognormal(
                sigma=float(stdev), mean=1) * float(weight) # weighted preference with degree of randomness
            self.preferences.append(weightedPreference)

    def pickTopProduct(self, products): # kano type formulas
        def calculateUtilityScore(attribute, preference, kanotype, direction):
            attribute = float(attribute)
            score = 0
            
            if direction == "lower is better": # reversed kano types
                if kanotype == 'basic': 
                    score = preference * (0 - math.e ** (2 * attribute - 1))
                elif kanotype == 'satisfier':
                    score = -preference * attribute
                elif kanotype == 'delighter':
                    score = preference * math.e ** (-2 * attribute - 1)
            else: # normal kano types
                if kanotype == 'basic':
                    score = preference * (0 - math.e ** (-2 * attribute - 1))
                elif kanotype == 'satisfier':
                    score = preference * attribute
                elif kanotype == 'delighter':
                    score = preference * math.e ** (2 * attribute - 1)

            return score
       

        if self.ownedProductRemainingLifespan > 0:
            self.ownedProductRemainingLifespan -= self.monthsPerTick
            
        else:
            # utility score calculation
            result = {}
            for idx, product in enumerate(products): # splitting the 1st value to idx, 2nd to product
                sum = 0
                for attribute, preference, kanotype, direction in zip(product.valueList, self.preferences, self.kanotypes, self.direction): # loop through all at same time in parallel
                    sum += calculateUtilityScore(attribute, preference, kanotype, direction)  # figures out score based on kanotype
                result[idx] = sum # once the score is found, consumer gets list of all products and how they are scored

            chosenIdx = max(result, key=result.get) # consumer choice of product that has best score
            products[chosenIdx].buy() # consumers buy product
            self.ownedProductRemainingLifespan = products[chosenIdx].lifespan  * np.random.exponential() #Changed to multiply by random.exp
            self.bestProducer = chosenIdx

class Product:
    def __init__(self, valueList, name):
        self.name = name
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.monthlySales = 0
        self.sales = 0  # The total amount of products that have been sold
        self.price = valueList[1]  # The price of the product
        self.productioncost = 0
        self.valueList = valueList
        self.lifespan = float(valueList[0]) 
        self.remainingLifespan = 0

    def buy(self):
        self.sales += 1
        self.monthlySales += 1
        self.remainingLifespan = 0
    
    def resetmonthlySales(self): # remove?
        self.monthlySales = 0




class Attribute:
    def __init__(self, name, kano, direction, stdev, weight): # data table columns, product attributes
        self.name = name
        self.kanotype = kano
        self.direction = direction
        self.stdev = stdev
        self.weight = weight

    def setkanotype(self, type):
        self.kanotype = type


class Simulation:
    def __init__(self, table, consumers, months, cost, monthsPerTick):
        self.df = table
        self.consumers = consumers  # number of consumers
        self.months = months  # number of months in simulation
        self.cost = cost
        self.monthsPerTick = monthsPerTick
        self.ticks = int(months/monthsPerTick) # prevents non integer months

        self.profitPerSale = int(self.df.iat[1, 5]) - self.cost # profit calculation

        self.attributeDF = self.df.iloc[:, 0:5] # splits data table into attributes dataframe

        self.productDF = self.df.iloc[:, 5:] # splits data table into product dataframe

        self.setAttributes() # set attributes
        self.setProducts() # set producers

        self.profitDF = {'Time (Months)': [], 'Profit ($)': []} # dict with time and profit for graphing

        self.noncumulativeprofitDF = {'Time (Months)': [], 'Profit ($)': []} # dict with time and non cumulative profit for graphing

        self.consumers = [Consumer(
                self.df['Spread'], self.df['Weight'], self.df['Kanotype'], self.df['Direction'], self.monthsPerTick) for _ in range(consumers)] # for amount of customers specified

        for i in range(self.ticks): # loop that runs every tick
            for consumer in self.consumers:
                consumer.pickTopProduct(self.products) # for every consumer in the list, calls pickTopProduct with list of products in the simulation
            self.profitDF['Time (Months)'].append(i*self.monthsPerTick) # sets month for x axis on graph
            self.profitDF['Profit ($)'].append(self.products[0].sales * self.profitPerSale) # sets profit for y axis
            # -------------------------
            self.noncumulativeprofitDF['Time (Months)'].append(i*self.monthsPerTick) # sets month for x axis on graph
            self.noncumulativeprofitDF['Profit ($)'].append(self.products[0].monthlySales * self.profitPerSale) # sets profit for y axis
            self.products[0].resetmonthlySales()  #Consider setting equal to zero rather than calling function
            # --------------------------

    def setAttributes(self):
        attributes = []
        for _, row in self.attributeDF.iterrows():
            attribute = None
            if not None in row.values:
                attribute = Attribute(*row.values)
            print(attribute)
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

    def getNonCumulativeProfitData(self):
        return self.noncumulativeprofitDF

    def getMarketShares(self):
        ms = {'Product Name': [], 'Sales': []}
        for product in self.products:
            ms['Product Name'].append(product.name)
            ms['Sales'].append(product.sales)
        df = pd.DataFrame(ms)
        return df

# -------------------------------------------------------


controls = dbc.Card(
    [
        dbc.Button('Apply', id='submit-button', color='primary',
                   block=True, className='mr-1')
    ],
    body=True,
)

# -----------    page layout   ------------------------

instructions = ['Be sure to fill in every cell, or the program won\'t run.',
                'Hover over column names to see additional information.',
                'Rename products by clicking the pencil icon in the header; click the trash icon to remove.',
                'Keep all Weight and Spread values between 0 and 10.',
                'Set Spread to a low initial value. Increase it the more consumers would disagree on the importance (weight) of a given attribute.',
                'Hover over graphs to see detail. You should see peaks in the graphs every [Lifespan] years.',
                '!! Your data will not save when you reload the page !!']

kanotooltip = [
    'Basic: A necessary attribute that does not impact consumer\'s happiness if it is included, but greatly dissatisfies consumers if it is absent.',
    'Satisfier: An attribute that is expected to be included in a product, and its effect on consumer satisfaction increases linearly with its inclusion.',
    'Delighter: A luxury attribute that is nice to have, it greatly increases consumer satisfaction if included. If absent, the consumer does not miss it.'
]

application.layout = html.Div([
    dbc.Row(dbc.Col(html.H1("ABM Market Simulator"),
                    style={"textAlign": "center"})),
    dbc.Row(dbc.Col(html.P("Welcome to the ABM Market Simulator, where you will simulate your product in the market."),
                    style={"textAlign":"center", "marginLeft": "75px","marginRight":"75px"})),
    dbc.Row(dbc.Col(html.P("You will assume the role of the producer developing a new product, and will enter information about the product and its competitors. Consumers will then choose which products to purchase, revealing trends in market share and your new product's profits."),
                    style={"textAlign":"center", "marginLeft": "75px","marginRight":"75px"})),
    dbc.Row(dbc.Col(children=[html.Ul(id='list', children=[html.Li(i) for i in instructions])],
                    style={"textAlign":"left", "marginLeft": "75px","marginRight":"60px"})),

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

                        {'name': 'Weight', # swapped places with spread column
                         'id': 'Weight',
                         'deletable': False,
                         'renamable': False,
                         'type': 'numeric'},

                         {'name': 'Spread',
                         'id': 'Spread',
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
                            'Attribute': 'Lifespan (months)',
                            'Kanotype': 'satisfier',
                            'Direction': 'higher is better',
                            'Spread': '5',
                            'Weight': '5',
                            'NewProduct': '12',
                            'Competitor-1': '3'
                        }]+[
                        {
                            'Attribute': 'Price',
                            'Kanotype': 'satisfier',
                            'Direction': 'lower is better',
                            'Spread': '5',
                            'Weight': '5',
                            'NewProduct': '20',
                            'Competitor-1': '50'
                        }]+[
                        {
                            'Attribute': None,
                            'Kanotype': None,
                            'Direction': 'higher is better',
                            'Spread': None,
                            'Weight': None,
                            'NewProduct': None,
                            'Competitor-1': None
                        }
                        for i in range(1) # how many additional attributes to make by default
                    ],
                    editable=True,
                    row_deletable=True,

                    tooltip_header={
                        'Kanotype': 'Basic: necessary, Satisfier: expected, Delighter: nice to have',
                        # 'Kanotype': html.Ul(id='list', children=[html.Li(i) for i in kanotooltip]),
                        'Direction': 'For positive attributes, higher score is better vs. negative attributes, where lower score is better',
                        'Spread': 'Number in the range of 0 - 10',
                        'Weight': 'Number in the range of 1 - 10',
                        'NewProduct': 'Besides price, use number in range of 0 - 10'
                    },

                    style_header={
                    'backgroundColor': 'rgb(126, 182, 196)',
                    'color':'darkslategrey',
                    'fontWeight': 'bold'
                    },

                    css=[{"selector": ".Select-menu-outer",
                          "rule": "display: block !important"}],
                    

                ),
                

                dbc.Form(
                    [
                        dbc.Button('Add Attribute', id='add-row-button',
                                   n_clicks=0, className="mx-3"),
                        dbc.FormGroup(
                            [
                                dbc.Label("Consumers", className="mr-2"),
                                dbc.Input(
                                    id='consumers-in-market', type='number', value=1000, max=5000),
                            ],
                            className="mr-3",
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Months", className="mr-2"),
                                dbc.Input(id='months', value=36,
                                          type='number'),
                            ],
                            className="mr-3",
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Months/Tick", className="mr-2"),
                                dbc.Input(
                                    id='monthsPerTick', value=1, type='number'),
                            ],
                            className="mr-3",
                        ),
                        dbc.FormGroup(
                            [
                                dbc.Label("Cost", className="mr-2"),
                                dbc.Input(
                                    id='production-cost', placeholder='Enter production cost', type='number',value=10),
                            ],
                            className="mr-5",
                        ),
                        
                        dbc.Button('Run Simulation',
                                   id='run-sim', color="success"),
                    ],
                    inline=True, className='my-2'),
            ]),

                width=12, style={'backgroundColor': 'rgb(45, 101, 115)'}),


            dbc.Col(html.Div(dcc.Graph(id='pie-chart')), width=4),
            dbc.Col(html.Div(dcc.Graph(id='line-graph')), width=4),
            dbc.Col(html.Div(dcc.Graph(id='bar-graph-noncum')), width=4)
            ])
])


# ------------------ end of layout --------------------


@application.callback(  # adds attributes
    Output('adding-rows-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns}) # TODO: should this set the cells equal to None?
    return rows


prevent_initial_call = True


@application.callback(  # adds products
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


@application.callback(
    Output('pie-chart', 'figure'),
    Output('line-graph', 'figure'),
    Output('bar-graph-noncum', 'figure'),
    Input('run-sim', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'),
    State('consumers-in-market', 'value'),
    State('production-cost', 'value'),
    State('months', 'value'),
    State('monthsPerTick', 'value'))
    
def generate_chart(n_clicks, table, columns, consumers, cost, months, monthsPerTick):
    if n_clicks is None:
        raise PreventUpdate
    else:
        df = pd.DataFrame.from_records(table, columns=[c['id'] for c in columns])
        sim = Simulation(df, consumers, int(months), cost, monthsPerTick)

        ms = sim.getMarketShares()
        pie = px.pie(ms, values='Sales', names='Product Name',hover_name='Product Name', title='Market Share', color_discrete_sequence=px.colors.qualitative.Prism, ) # pie chart: market share

        profit = sim.getProfitData()
        line = px.line(profit, x="Time (Months)", y="Profit ($)", title='New Product Cumulative Profit', color_discrete_sequence=px.colors.qualitative.Prism) # line graph: profit
       
        noncumulativeprofit = sim.getNonCumulativeProfitData()
        noncumbar = px.line(noncumulativeprofit, x="Time (Months)", y="Profit ($)", title='New Product Non-Cumulative Profit', color_discrete_sequence=px.colors.qualitative.Prism) # line graph: profit non cumulative
        
        return pie, line, noncumbar


prevent_initial_call = True


suppress_callback_exceptions=False

# -------------------------------------------------------

if __name__ == '__main__':
    application.run_server(debug=True, dev_tools_hot_reload=False)
