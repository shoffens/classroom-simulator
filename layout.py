import dash
from dash.dependencies import Input, Output, State
import dash_table
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash(__name__)

app.layout = html.Div([
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

    dcc.Graph(id='adding-rows-graph')
])


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
            'type': 'heatmap',
            'z': [[row.get(c['id'], None) for c in columns] for row in rows],
            'x': [c['name'] for c in columns]
        }]
    }


if __name__ == '__main__':
    app.run_server(debug=True)
