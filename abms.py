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
start_time = time.time() # tracks execution time

app = dash.Dash(external_stylesheets=[dbc.themes.SOLAR]) # bootstrap style sheet

## -----------------

# table with dynamic columns and rows
# prompt user to enter how many columns and rows

## -----------------

class Consumer:
    def __init__(self, attributes):
        self.preferences = attributes # Randomly generated, based on normal distributions; used in utility function
        self.bestProducer = 0 # Initially, all consumers are considered to be consumers of product 0
        self.productLifespan = -1 # A lifespan of less than 0 means the consumer no longer owns a product, initializes
        
    def setpreferences(self, weight): 
        self.preferences = np.random.normal(scale=1) * weight # creates preferences for consumer, based on stddev of 0-1, multipled by weight

    def setProductLifespan(self, productLifespans):
        self.productLifespan = max(self.productLifespans) * 2.5 * 12 # 2.5 sets it to be a 10x multiplier for the inputted product lifespan


class Producer:
    def __init__(self, productLifespans):
        self.avgProductLifespan = -1 # product-lifespan; The average amount of time (in years) before the product breaks
        self.productLifespans = productLifespans # list of all lifespans for products (user input)
        self.profit = 0 # total profit accumulated for new product (starting with no profit)
        self.sales = 0 # The total amount of products that have been sold
        self.price = 0 # The price of the product
        self.productvalues = 0
        self.productlife = 0
        self.productioncost = 0
        #self.productAttributes = productAttributes # A list of attribute values for this producer's product (user input)

    def setavgProductLifespan(self, average):
        self.avgProductLifespan = average(self.avgProductLifespan) * 365 # separate

    class ProductAttributes:
        def __init__ (self):
            self.spread = range(0,1)
            self.weight = [1,2,3,4,5,6,7,8,9,10]
            self.kanotype
            # productAttributes = {
            #     'spread': range(0,1), 
            #     'weight': [1,2,3,4,5,6,7,8,9,10],
            #     'kanotypes':['basic','satisfier','delighter']
            #     }

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

    def setproductLifespan(self,productLifespan,days): # Decrement the lifespan of the product accordingly
        self.productLifespan = (productLifespan - days) 
       
    
    def setdays(self,ticks,daysPerTick): # Update the amount of days that have elapsed
        self.days = ticks * (daysPerTick + 1)
        return ticks # update the simulation graphs to current day  ----------------------- UPDATE once plots are made

    def generate_df(user_input): # generates dataframe CHANGE ! ---------------------------------------------------------------------
        created_dict = {'col': user_input, 'value': user_input * 3}
        df = pd.DataFrame(created_dict)
        return df

    # make a function, using loop, that calculates all data i need to graph based on inputs
    # generate dataframe to be used in graphing/figures


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

def productstext():
    return html.Div([ 
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.P("New Product and Competitors")
                ], style={'textAlign': 'center'})
            ])
        ),
    ])

# slider function for weight and standard dev
def sliderS(name, id, min, max, step):
    return html.Div(
            [
                dbc.Label(name, className = 'mx-3'),
                html.Br(),
                html.Div(
                    [dcc.Slider(
                    id=id, min=min, max=max, step=step, value=0.5,marks={0:'0', 1:'1'},
                    className = 'mx-3',
                    tooltip={'always_visible': True, 'placement': 'bottom'}),
                    ],)
                
        ]
    )

def sliderW(name, id, min, max, step):
    return html.Div(
        [
            dbc.Label(name, className = 'mx-3'),
            html.Br(),
            html.Div(
                [dcc.Slider(
                id=id, min=min, max=max, step=step, value=5,marks={1:'1', 10:'10'},
                tooltip={'always_visible': True, 'placement': 'bottom'})
                ],)
            
    ]
)
# kanotype input
def kanotypeInput(name):
    return html.Div(
        [ 
            dcc.Dropdown(
                id=id, 
                options=[
                {'label': 'basic', 'value': 'basic'},
                {'label': 'satisfier', 'value': 'satisfier'},
                {'label': 'delighter', 'value': 'delighter'}],
                value='basic'),
    ]
)

# attribute card function that takes in the attribute name and number
# returns attribute info, weight, standard dev slider into one card
def attributeCard(name, attrNum):
    return dbc.Card(
        [
            dbc.Row([dbc.Col(html.Div(name)), dbc.Col(dcc.Input(id=f"input{attrNum}", type="text", placeholder=f"Attribute {attrNum}", size='12',className='mx-3'))]),
            # dbc.Row(
                # [
                    # html.Br(),
                    html.Div(
                        sliderW("Weight", f"Weight {attrNum}", 1, 10, 1),
                        ), 
                        sliderS("Standard Deviation", f"Standard Deviation {attrNum}", 0, 1, .05),
                        # kanotypeInput('name')

                
        ])

def productNameCard(name,prodName):
    return dbc.Card(
        [
            dbc.Row([dbc.Col(html.Div(name)), dbc.Col(dcc.Input(id=f'input{prodName}', type='text', placeholder=f'Product Name', className='mr-4'))])
        ]
    )

def productValueCard(value):
    return dbc.Card(
        [
            dbc.Row([dbc.Col(html.Div(value)),dbc.Col(dcc.Input(id='',type='number',placeholder='',className='mr-4'))])
        ]
    )

# -------------------------------------------------------

# dcc.Store(id='memory')

# -------------------------------------------------------

controls = dbc.Card( # defines controls, does not put them on screen
    [
    dbc.Button('Apply', id='submit-button', color='primary', block=True, className='mr-1')
    ],
    body=True,
)



# -----------    page layout   ------------------------

# app.layout  = html.Div ([

#     html.Div([
#         html.H1(children='Market Simulator',
#         style = {'textAlign': 'center'}
#         )],
#     ),
    



# ])

# app.layout = html.Div(children=[
#     html.Div(className='row',  # Define the row element
#             children=[
#                 html.Div(className='four columns div-user-controls',),  # Define the left element
#                 html.Div(className='eight columns div-for-charts bg-grey')  # Define the right element
#                 ])
#             ])

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
             'deletable': False,
             'renamable': False},

            {'name': 'Stdev',
             'id': 'Stdev',
             'deletable': False,
             'renamable': False},

            {'name': 'Weight',
             'id': 'Weight',
             'deletable': False,
             'renamable': True},
        ],
        # columns=[{
        #     'name': 'Column {}'.format(i),
        #     'id': 'column-{}'.format(i),
        #     'deletable': True,
        #     'renamable': True
        # } for i in range(1, 5)],
        data=[
            {'column-{}'.format(i): (j + (i-1)*5) for i in range(1, 5)}
            for j in range(5)
        ],
        editable=True,
        row_deletable=True
        
),

html.Button('Add Attribute', id='add-row-button', n_clicks=0),

   
]), width=7,style={'background-color': 'rgb(45, 101, 115)'}),


dbc.Col(html.Div(dcc.Graph(id='adding-rows-graph')), width=5),
])
])



# ------------------ end of layout --------------------

@app.callback(
    Output('adding-rows-table', 'data'),
    Input('add-row-button', 'n_clicks'),
    State('adding-rows-table', 'data'),
    State('adding-rows-table', 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@app.callback(
    Output('adding-rows-table', 'columns'),
    Input('add-column-button', 'n_clicks'),
    State('adding-rows-name', 'value'),
    State('adding-rows-table', 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns


@app.callback(
    Output('adding-rows-graph', 'figure'),
    Input('adding-rows-table', 'data'),
    Input('adding-rows-table', 'columns'))
def display_output(rows, columns):
    return {
        'data': [{
            'type': 'line',
            'z': [[row.get(c['id'], None) for c in columns] for row in rows], # change to profit calc
            'x': [c['name'] for c in columns] # change to profit calc
        }]
    }

    # new callback for adding new graph of market share - pie chart



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