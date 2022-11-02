import pypath

from red_moose.modeling.quantlib_calculator import OptionArgs, OptionProfile, OptionCombinator
from red_moose.ui.dash_utils import generate_table, make_table_dash
import QuantLib as ql
import base64
import datetime
import io
import dash
import plotly.graph_objects as go
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import pandas as pd

pd.options.plotting.backend = "plotly"

"""
start = 127
stop = 135
periods = 10
settle = ql.Date(13, ql.November, 2020)
expiry = ql.Date(23, ql.December, 2020)

df = OptionProfile.sigma_range(
    OptionArgs(
        underlying=ql.SimpleQuote(123.0),
        irate=ql.SimpleQuote(1.5 / 100.),
        sigma=ql.SimpleQuote(2 / 100.),
        settle=settle,
        expiry=expiry,
        strike=130.0,
        quantity=2,
        opttype=ql.Option.Call),
    14,
    22,
    10
)

print(df)
df['settle'] = df.settle.apply(lambda x: x.to_date())
df['expiry'] = df.expiry.apply(lambda x: x.to_date())

fig = df.npv.plot()
"""


def combinator_date():
    # straddle
    start = 127
    stop = 135
    periods = 10
    settle = ql.Date(13, ql.November, 2020)
    expiry = ql.Date(23, ql.December, 2020)

    dfc = OptionProfile.date_range(
        OptionArgs(
            underlying=ql.SimpleQuote(130.0),
            irate=ql.SimpleQuote(1.5 / 100.),
            sigma=ql.SimpleQuote(2 / 100.),
            settle=settle,
            expiry=expiry,
            strike=130.0,
            quantity=1,
            opttype=ql.Option.Call)
    )
    dfp = OptionProfile.date_range(
        OptionArgs(
            underlying=ql.SimpleQuote(130.0),
            irate=ql.SimpleQuote(1.5 / 100.),
            sigma=ql.SimpleQuote(2 / 100.),
            settle=settle,
            expiry=expiry,
            strike=130.0,
            quantity=1,
            opttype=ql.Option.Put)
    )

    oc = OptionCombinator.create_settle([dfc, dfp])
    df = oc.combine()
    df.reset_index(inplace=True)
    df['settle'] = df.settle.apply(lambda x: x.to_date())
    # df['expiry'] = df.expiry.apply(lambda x: x.to_date())
    return df


def combinator_sigma():
    # straddle
    start = 12.7 / 100.
    stop = 13.5 / 100.
    periods = 10
    settle = ql.Date(13, ql.November, 2020)
    expiry = ql.Date(23, ql.December, 2020)

    dfc = OptionProfile.sigma_range(
        OptionArgs(
            underlying=ql.SimpleQuote(130.0),
            irate=ql.SimpleQuote(1.5 / 100.),
            sigma=ql.SimpleQuote(2 / 100.),
            settle=settle,
            expiry=expiry,
            strike=130.0,
            quantity=1,
            opttype=ql.Option.Call),
        start, stop, periods
    )
    dfp = OptionProfile.sigma_range(
        OptionArgs(
            underlying=ql.SimpleQuote(130.0),
            irate=ql.SimpleQuote(1.5 / 100.),
            sigma=ql.SimpleQuote(2 / 100.),
            settle=settle,
            expiry=expiry,
            strike=130.0,
            quantity=1,
            opttype=ql.Option.Put),
        start, stop, periods
    )

    oc = OptionCombinator.create_sigma([dfc, dfp])
    df = oc.combine()
    df.reset_index(inplace=True)
    df['settle'] = df.settle.apply(lambda x: x.to_date())
    # df['expiry'] = df.expiry.apply(lambda x: x.to_date())
    return df


def combinator_underlying():
    # straddle
    strike = 130.0
    start = strike - 5
    stop = strike + 5
    periods = 10
    settle = ql.Date(13, ql.November, 2020)
    expiry = ql.Date(23, ql.December, 2020)

    dfc = OptionProfile.underlying_range(
        OptionArgs(
            underlying=ql.SimpleQuote(130.0),
            irate=ql.SimpleQuote(1.5 / 100.),
            sigma=ql.SimpleQuote(2 / 100.),
            settle=settle,
            expiry=expiry,
            strike=130.0,
            quantity=1,
            opttype=ql.Option.Call),
        start, stop, periods
    )
    dfp = OptionProfile.underlying_range(
        OptionArgs(
            underlying=ql.SimpleQuote(130.0),
            irate=ql.SimpleQuote(1.5 / 100.),
            sigma=ql.SimpleQuote(2 / 100.),
            settle=settle,
            expiry=expiry,
            strike=130.0,
            quantity=1,
            opttype=ql.Option.Put),
        start, stop, periods
    )

    oc = OptionCombinator.create_underlying([dfc, dfp])
    df = oc.combine()
    df.reset_index(inplace=True)
    df['settle'] = df.settle.apply(lambda x: x.to_date())
    # df['expiry'] = df.expiry.apply(lambda x: x.to_date())
    return df


sdf = combinator_sigma()
df = combinator_date()
udf = combinator_underlying()

external_stylesheets = [dbc.themes.BOOTSTRAP]  # ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Positions CSV: Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '90%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload'),
    dcc.RadioItems(
        id='radios',
        options=[
            {'label': 'sigma', 'value': 'sigma'},
            {'label': 'settle_date', 'value': 'settle_date'},
            {'label': 'underlying', 'value': 'underlying'}
        ],
        value='settle_date'
    ),
    dcc.Dropdown(
        id='my-dropdown',
        options=[
            {'label': 'Delta', 'value': 'Delta'},
            {'label': 'Gamma', 'value': 'Gamma'},
            {'label': 'Vega', 'value': 'Vega'},
            {'label': 'Theta', 'value': 'Theta'},
            {'label': 'NPV', 'value': 'NPV'}
        ],
        value='NPV'
    ),
    dcc.Graph(id='my-graph'),
    # dcc.Graph(id='theta_graph'),
    # dcc.Graph(id='delta_graph'),
    # dcc.Graph(id='npv_graph'),
    # html.Div(dcc.Input(id='input-on-submit', type='hidden')),
    # html.Button('NPV Plot', id='submit-val', n_clicks=0),
    # html.Button('Delta Plot', id='submit-sigma', n_clicks=0),
    # html.Button('Theta Plot', id='submit-theta', n_clicks=0),
    # html.Div(id='container-button-basic',children=''),
    make_table_dash(udf)
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            xdf = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([

        dcc.Graph(
            figure=go.Figure(data=[
                go.Bar(name=xdf.columns.values[0], x=pd.unique(df['Make']), y=df['Score'], text=df['Score'],
                       textposition='auto'),
            ])
        ),
    ])


@app.callback(dash.dependencies.Output('output-data-upload', 'children'),
              [dash.dependencies.Input('upload-data', 'contents')],
              [dash.dependencies.State('upload-data', 'filename'),
               dash.dependencies.State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(
    dash.dependencies.Output('my-graph', 'figure'),
    [dash.dependencies.Input('my-dropdown', 'value'),
     dash.dependencies.Input('radios', 'value')])
def update_graph(selected_dropdown_value, radio_value):
    if radio_value == 'settle_date':
        cdf = df.set_index('settle')
    elif radio_value == 'sigma':
        cdf = sdf.set_index('sigma')
    else:
        cdf = udf.set_index('underlying')
    router = {
        'Delta': lambda: cdf.delta.plot(),
        'Gamma': lambda: cdf.gamma.plot(),
        'Vega': lambda: cdf.vega.plot(),
        'NPV': lambda: cdf.npv.plot(),
        'Theta': lambda: cdf.theta.plot()
    }
    return router[selected_dropdown_value]()


"""
@app.callback(
    dash.dependencies.Output('delta_graph', 'figure'),
    [dash.dependencies.Input('submit-sigma', 'n_clicks')],
    [dash.dependencies.State('input-on-submit', 'value')])
def plot_delta(a, b):
    cdf = df.set_index('settle')
    return cdf.delta.plot()

@app.callback(
    dash.dependencies.Output('theta_graph', 'figure'),
    [dash.dependencies.Input('submit-theta', 'n_clicks')],
    [dash.dependencies.State('input-on-submit', 'value')])
def plot_theta(a, b):
    cdf = df.set_index('settle')
    return cdf.theta.plot()

@app.callback(
    dash.dependencies.Output('npv_graph', 'figure'),
    [dash.dependencies.Input('submit-val', 'n_clicks')],
    [dash.dependencies.State('input-on-submit', 'value')])
def plot_npv(a, b):
    cdf = df.set_index('settle')
    return cdf.npv.plot()
"""

# app.layout = make_table_dash(df)
if __name__ == '__main__':
    app.run_server(debug=True,
                   port=6121,
                   # host='ec2-18-214-12-198.compute-1.amazonaws.com',
                   dev_tools_ui=True,
                   dev_tools_hot_reload=True,
                   threaded=True)
