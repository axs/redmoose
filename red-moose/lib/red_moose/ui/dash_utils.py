import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table


def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


def make_table_dash(df):
    return dash_table.DataTable(
        id='table',
        css=[{'selector': '.row', 'rule': 'margin: 0'}],
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        export_format="csv",
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        }
    )


def make_card(alert_message, color, cardbody, style_dict=None):
    return dbc.Card([dbc.Alert(alert_message, color=color), dbc.CardBody(cardbody)
                     ], style=style_dict)


def make_item(button, cardbody, i):
    # This function makes the accordion items
    return dbc.Card([
        dbc.CardHeader(
            html.H2(
                dbc.Button(
                    button,
                    color="link",
                    id=f"group-{i}-toggle"))),
        dbc.Collapse(
            dbc.CardBody(cardbody),
            id=f"collapse-{i}")])


def make_table(id, dataframe, lineHeight='17px', page_size=5):
    return dash_table.DataTable(
        id=id,
        css=[{'selector': '.row', 'rule': 'margin: 0'}],
        columns=[
            {"name": i, "id": i} for i in dataframe.columns
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'},
        style_cell={'textAlign': 'left'},
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': lineHeight
        },

        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_cell_conditional=[
            {'if': {'column_id': 'title'},
             'width': '130px'},
            {'if': {'column_id': 'post'},
             'width': '500px'},
            {'if': {'column_id': 'datetime'},
             'width': '130px'},
            {'if': {'column_id': 'text'},
             'width': '500px'}],
        page_current=0,
        page_size=page_size,
        page_action='custom',
        filter_action='custom',
        filter_query='',
        sort_action='custom',
        sort_mode='multi',
        sort_by=[]
    )  # end table
