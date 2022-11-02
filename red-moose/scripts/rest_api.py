import pypath
from typing import Optional, Dict
from fastapi import FastAPI, Request
from red_moose.persistence.queries import Queries
from red_moose.modeling.portfolio_risk import PortfolioRisk
from red_moose.modeling.quantlib_calculator import OptionArgs, OptionProfile, OptionCombinator
import QuantLib as ql
from datetime import datetime

app = FastAPI()


# uvicorn rest_api:app --reload

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/pos_life_pnl/{account_id}")
def position_lifetime_pnl(account_id: str, history: bool = False):
    return Queries.position_pnl(account_id, history=history)


@app.post("/portfolio_risk/")
async def portfolio_risk(input_json: dict):
    """
    <pre>
    Args:
        input_json ={"underlying": {"short_rate": 0.01,
          "initial_value": 110.0,
          "volatility": 0.18,
          "pricing_date": "20201123"},
         "positions": [{"quantity": 1,
           "strike": 105.0,
           "maturity": "20210630",
           "payoff": "put"},
          {"quantity": 2, "strike": 115.0, "maturity": "20210630", "payoff": "call"},
          {"quantity": -1, "strike": 120.0, "maturity": "20210630", "payoff": "call"}]}
    </pre>
    """
    underlying = input_json.get('underlying')
    underlying['pricing_date'] = datetime.strptime(underlying['pricing_date'], '%Y%m%d')
    positions = input_json.get('positions')
    pr = PortfolioRisk(**underlying)
    enriched_positions = {}
    for i, p in enumerate(positions):
        p['maturity'] = datetime.strptime(p['maturity'], '%Y%m%d')
        enriched_positions[f"{p['payoff']}_{i}"] = pr.define_position(**p)
    res = pr.define_portfolio(enriched_positions)
    results = pr.volatility_risk_report(res)
    return [r.to_dict(orient='records') for r in results]


@app.post("/option_profile/")
def option_profile(input_json: dict):
    """
    <pre>
    x_axis is one of underlying, sigma, settle
    Args:
        input_json ={
        "x_axis": "underlying",
                    "start" : 119.0,
            "stop": 126.0,
            "periods": 10,
        "options": [ {
            "underlying": 123.0,
            "irate" : 0.015,
            "sigma" : 0.02,
            "settle" : "20210306",
            "expiry": "20210423",
            "strike": 130.0,
            "opttype": "call",
            "quantity": 2
            }]
        }
        input_json ={
                "x_axis": "sigma",
                            "start" : 0.12,
                    "stop": 0.23,
                    "periods": 10,
                "options": [ {
                    "underlying": 123.0,
                    "irate" : 0.015,
                    "sigma" : 0.02,
                    "settle" : "20210306",
                    "expiry": "20210423",
                    "strike": 130.0,
                    "opttype": "call",
                    "quantity": 5
                    }]
                }
    </pre>
    """
    factory = {
        'underlying': (lambda x: OptionCombinator.create_underlying(x),
                       lambda x, b, e, p: OptionProfile.underlying_range(x, b, e, p)),
        'settle': (lambda x: OptionCombinator.create_settle(x),
                   lambda x: OptionProfile.date_range(x)),
        'sigma': (lambda x: OptionCombinator.create_sigma(x),
                  lambda x, b, e, p: OptionProfile.sigma_range(x, b, e, p)
                  )
    }
    oargs = [OptionArgs.from_dict(o) for o in input_json['options']]
    combinator, prof = factory[input_json['x_axis']]
    profile_results = [prof(o,
                            input_json.get('start'),
                            input_json.get('stop'),
                            input_json.get('periods')) for o in
                       oargs]
    oc = combinator(profile_results)
    df = oc.combine()
    df.reset_index(inplace=True)
    try:
        df['settle'] = df['settle'].astype(str)
    except Exception as e:
        pass
    try:
        df['expiry'] = df['expiry'].astype(str)
    except Exception as e:
        pass
    return df.to_dict(orient='records')
