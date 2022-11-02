import logging
from typing import Dict, List

import QuantLib as ql
import attr
from datetime import datetime
import numpy as np
import pandas as pd

from red_moose.rm_types import OptionProfileResults

log = logging.getLogger(__name__)


@attr.s(auto_attribs=True, slots=True)
class OptionArgs:
    underlying: ql.SimpleQuote
    irate: ql.SimpleQuote
    sigma: ql.SimpleQuote
    settle: ql.Date
    expiry: ql.Date
    strike: float
    opttype: ql.Option
    engine: str = attr.ib(default='analytic')
    style: str = attr.ib(default='european')
    quantity: int = attr.ib(default=1)

    @classmethod
    def from_dict(cls, i: Dict):
        """
        Args:
            i: {
                        "underlying": 123.0,
                        "irate" : 1.5 / 100.0,
                        "sigma" : 2 / 100.0,
                        "settle" : "20210306",
                        "expiry": "20210423",
                        "strike": 130.0,
                        "opttype": "call"
                        }

        Returns:
        """
        otype_map = {
            'call': ql.Option.Call,
            'put': ql.Option.Put
        }
        return cls(underlying=ql.SimpleQuote(i['underlying']),
                   irate=ql.SimpleQuote(i['irate']),
                   sigma=ql.SimpleQuote(i['sigma']),
                   settle=ql.Date.from_date(datetime.strptime(i['settle'], '%Y%m%d')),
                   expiry=ql.Date.from_date(datetime.strptime(i['expiry'], '%Y%m%d')),
                   strike=i['strike'],
                   quantity=i.get('quantity', 1),
                   opttype=otype_map[i['opttype'].lower()]
                   )

    @staticmethod
    def from_dataframe(df) -> List:
        """Assume dataframe is ...
               underlying  irate  sigma    settle    expiry  strike opttype
                    123.0  0.015   0.02  20210306  20210423   130.0    call
        Args:
            df:

        Returns: List[OptionArgs]
        """
        return [OptionArgs.from_dict(i) for i in df.to_dict(orient='records')]


class OptionCalculator:
    """
    today = ql.Date(7, ql.March, 2014)
    ql.Settings.instance().evaluationDate = today
    option = ql.EuropeanOption(ql.PlainVanillaPayoff(ql.Option.Call, 100.0),
                    ql.EuropeanExercise(ql.Date(7, ql.June, 2014)))
    u = ql.SimpleQuote(100.0)
    r = ql.SimpleQuote(0.01)
    sigma = ql.SimpleQuote(0.20)
    riskFreeCurve = ql.FlatForward(0, ql.TARGET(),ql.QuoteHandle(r), ql.Actual360())
    volatility = ql.BlackConstantVol(0, ql.TARGET(),
                                             ql.QuoteHandle(sigma), ql.Actual360())
    process = ql.BlackScholesProcess(ql.QuoteHandle(u),
                                             ql.YieldTermStructureHandle(riskFreeCurve),
                                             ql.BlackVolTermStructureHandle(volatility))
    engine = ql.AnalyticEuropeanEngine(process)
    option.setPricingEngine(engine)
    option.NPV()
    """

    def __init__(self, option_args: OptionArgs):
        self.option_args = option_args
        settlementDate = self.option_args.settle
        ql.Settings.instance().evaluationDate = settlementDate
        riskFreeRate = ql.FlatForward(0,
                                      ql.TARGET(),
                                      ql.QuoteHandle(self.option_args.irate),
                                      ql.Actual360())

        # market data
        volatility = ql.BlackConstantVol(0,
                                         ql.TARGET(),
                                         ql.QuoteHandle(self.option_args.sigma),
                                         ql.Actual360())
        # dividendYield = ql.FlatForward(settlementDate, 0.00, ql.Actual360())

        self.process = ql.BlackScholesProcess(ql.QuoteHandle(self.option_args.underlying),
                                              ql.YieldTermStructureHandle(riskFreeRate),
                                              ql.BlackVolTermStructureHandle(volatility))
        ex_lookup = {
            'american': lambda: ql.AmericanExercise(settlementDate, self.option_args.expiry),
            'european': lambda: ql.EuropeanExercise(self.option_args.expiry)
        }

        self.option = ql.VanillaOption(ql.PlainVanillaPayoff(self.option_args.opttype, self.option_args.strike),
                                       ex_lookup[self.option_args.style]())
        self.set_engine()

    def set_engine(self):
        gridPoints = 800
        timeSteps = 801
        # method: binomial
        binomial_engine = {'trigeorgis', 'lr', 'eqp', 'tian', 'jr', 'crr'}
        engine_lookup = {
            'binomial': lambda: ql.BinomialVanillaEngine(self.process,
                                                         self.option_args.engine,
                                                         timeSteps),
            'Barone-Adesi-Whaley': lambda: ql.BaroneAdesiWhaleyEngine(self.process),
            'Bjerksund-Stensland': lambda: ql.BjerksundStenslandEngine(self.process),
            'finitediff_american': lambda: ql.FDAmericanEngine(self.process, timeSteps, gridPoints),
            'finitediff_european': lambda: ql.FDEuropeanEngine(self.process, timeSteps, gridPoints),
            'analytic': lambda: ql.AnalyticEuropeanEngine(self.process),
            'integral': lambda: ql.IntegralEngine(self.process)
        }
        if self.option_args.engine in binomial_engine:
            e = 'binomial'
        elif self.option_args.engine == 'finitediff':
            e = f'{self.option_args.engine}_{self.option_args.style}'
        else:
            e = self.option_args.engine
        self.option.setPricingEngine(engine_lookup[e]())

    def calculate(self):
        try:
            npv = self.option.NPV()
        except Exception as e:
            log.exception(e)
            npv = None
        try:
            delta = self.option.delta()
        except Exception as e:
            log.exception(e)
            delta = None
        try:
            gamma = self.option.gamma()
        except Exception as e:
            log.exception(e)
            gamma = None
        try:
            vega = self.option.vega()
        except Exception as e:
            log.exception(e)
            vega = None
        try:
            theta = self.option.theta()
        except Exception as e:
            log.exception(e)
            theta = None
        return [npv, delta, gamma, vega, theta]

    def implied_vol(self, price):
        iv = None
        try:
            iv = self.option.impliedVolatility(price, self.process)
        except Exception as e:
            log.exception(e)
            pass
        return iv


class GreekCollector:
    def __init__(self):
        self.results = []

    def collect(self, calculator_results, calculator):
        calculator_results.append(float(calculator.option_args.underlying.value()))
        calculator_results.append(float(calculator.option_args.sigma.value()))
        calculator_results.append(calculator.option_args.settle)
        calculator_results.append(calculator.option_args.expiry)
        calculator_results.append(calculator.option_args.quantity)
        self.results.append(calculator_results)


class OptionProfile:
    GREEKS = ['npv', 'delta', 'gamma', 'vega', 'theta']
    COLUMNS = GREEKS + ['underlying', 'sigma', 'settle', 'expiry', 'quantity']

    @staticmethod
    def underlying_range(option_args: OptionArgs, start_price, stop_price, num_periods) -> OptionProfileResults:
        """
        Description: returns dataframes of greeks and NPV over ranges
        Args:
            option_args: option_args.underlying will be updated over the range
            start_price:
            stop_price:
            num_periods:

        Returns: dataframe of greeks and npv over given range of underlying prices
        """
        greek_collector = GreekCollector()
        for u in np.linspace(start_price, stop_price, num_periods):
            option_args.underlying = ql.SimpleQuote(u)
            c = OptionCalculator(option_args)
            r = c.calculate()
            greek_collector.collect(r, c)
        df = pd.DataFrame(columns=OptionProfile.COLUMNS, data=greek_collector.results)
        df.loc[:, OptionProfile.GREEKS] = df.loc[:, OptionProfile.GREEKS] * option_args.quantity
        return df

    @staticmethod
    def date_range(option_args: OptionArgs, *args) -> OptionProfileResults:
        """
        Description: returns dataframes of greeks and NPV over ranges
        Args:
            option_args: option_args.settle will be updated over the range

        Returns:
        """
        date_range = pd.date_range(start=option_args.settle.to_date(), end=option_args.expiry.to_date())
        greek_collector = GreekCollector()
        for d in date_range.to_pydatetime():
            option_args.settle = ql.Date.from_date(d)
            c = OptionCalculator(option_args)
            r = c.calculate()
            greek_collector.collect(r, c)
        df = pd.DataFrame(columns=OptionProfile.COLUMNS, data=greek_collector.results)
        df.loc[:, OptionProfile.GREEKS] = df.loc[:, OptionProfile.GREEKS] * option_args.quantity
        return df

    @staticmethod
    def sigma_range(option_args: OptionArgs, start_sigma, stop_sigma, num_periods) -> OptionProfileResults:
        greek_collector = GreekCollector()
        for s in np.linspace(start_sigma, stop_sigma, num_periods):
            option_args.sigma = ql.SimpleQuote(s)
            c = OptionCalculator(option_args)
            r = c.calculate()
            greek_collector.collect(r, c)
        df = pd.DataFrame(columns=OptionProfile.COLUMNS, data=greek_collector.results)
        df.loc[:, OptionProfile.GREEKS] = df.loc[:, OptionProfile.GREEKS] * option_args.quantity
        return df


class OptionCombinator:
    GREEKS = ['npv', 'delta', 'gamma', 'vega', 'theta']

    def __init__(self, index_column, opr: List[OptionProfileResults]):
        self.index_column = index_column
        self.opr = opr

    @classmethod
    def create_sigma(cls, opr: List[OptionProfileResults]):
        return cls('sigma', opr)

    @classmethod
    def create_settle(cls, opr: List[OptionProfileResults]):
        return cls('settle', opr)

    @classmethod
    def create_underlying(cls, opr: List[OptionProfileResults]):
        return cls('underlying', opr)

    def combine(self) -> OptionProfileResults:
        """
        Example:
              df = OptionProfile.date_range(
                          OptionArgs(
                              underlying=ql.SimpleQuote(123.0),
                              irate=ql.SimpleQuote(1.5 / 100.),
                              sigma=ql.SimpleQuote(2 / 100.),
                              settle=settle,
                              expiry=expiry,
                              strike=130.0,
                              opttype=ql.Option.Call)
                      )
              df2 = OptionProfile.date_range(
                          OptionArgs(
                              underlying=ql.SimpleQuote(123.0),
                              irate=ql.SimpleQuote(1.5 / 100.),
                              sigma=ql.SimpleQuote(2 / 100.),
                              settle=settle,
                              expiry=expiry,
                              strike=132.0,
                              opttype=ql.Option.Call)
                      )
              df2=df2.iloc[12:23].copy()
              oc = OptionCombinator('settle',[df,df2])
              oc.combine()
        Returns: summed up greeks and npv for combined OptionProfileResults on a common index_column
        """
        for df in self.opr:
            df.set_index(self.index_column, inplace=True)
        combined_df = [df[OptionCombinator.GREEKS] for df in self.opr]
        combined_df = sum(combined_df)
        combined_df.dropna(inplace=True)
        missing_cols = set(self.opr[0].columns) - set(OptionCombinator.GREEKS) - {'expiry', 'strike', 'quantity'}
        for m in missing_cols:
            combined_df[m] = self.opr[0][m]
        return combined_df
