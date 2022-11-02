import typing
import dx
import datetime as dt
from dx.valuation.derivatives_portfolio import derivatives_portfolio
import numpy as np


class PortfolioRisk:
    CALL_PAYOFF = 'np.maximum(instrument_values - strike, 0)'
    PUT_PAYOFF = 'np.maximum(strike - instrument_values, 0)'
    PATHS = 10000
    UNDERLYING_GBM = 'underyling_gbm'

    def __init__(self, **kwargs):
        self.risk_factors = dx.constant_short_rate('r', kwargs.get('short_rate'))

        # UNDERLYING
        self.initial_value = kwargs.get('initial_value')
        self.volatility = kwargs.get('volatility')

        self.mkt_env_1 = dx.market_environment('mkt_1', kwargs.get('pricing_date'))
        self.mkt_env_1.add_constant('initial_value', kwargs.get('initial_value'))
        self.mkt_env_1.add_constant('volatility', kwargs.get('volatility'))
        self.mkt_env_1.add_constant('final_date', self.mkt_env_1.pricing_date + dt.timedelta(days=180))
        self.mkt_env_1.add_constant('currency', 'USD')
        self.mkt_env_1.add_constant('frequency', 'W')
        self.mkt_env_1.add_constant('paths', PortfolioRisk.PATHS)
        self.mkt_env_1.add_curve('discount_curve', self.risk_factors)
        self.underyling_gbm = dx.geometric_brownian_motion(PortfolioRisk.UNDERLYING_GBM, self.mkt_env_1)

    def define_position(self, **kwargs) -> dx.derivatives_position:
        payoff_lookup = {
            'put': PortfolioRisk.PUT_PAYOFF,
            'call': PortfolioRisk.CALL_PAYOFF
        }
        mkt_opt = dx.market_environment('mkt_opt', self.mkt_env_1.pricing_date)
        mkt_opt.add_environment(self.mkt_env_1)
        mkt_opt.add_constant('maturity', kwargs.get('maturity'))
        mkt_opt.add_constant('strike', kwargs.get('strike'))
        opt = dx.derivatives_position(
            name=f"{kwargs.get('payoff')}_{kwargs.get('strike')}",
            quantity=kwargs.get('quantity'),
            underlyings=[PortfolioRisk.UNDERLYING_GBM],
            mar_env=mkt_opt,
            otype='American single',
            payoff_func=payoff_lookup[kwargs.get('payoff')])
        return opt

    def define_portfolio(self, positions: typing.Dict[str, dx.derivatives_position], **kwargs) -> derivatives_portfolio:
        self.mkt_env_1.add_constant('model', 'gbm')
        risk_factors = {PortfolioRisk.UNDERLYING_GBM: self.mkt_env_1}

        val_env = dx.market_environment('general', kwargs.get('pricing_date', self.mkt_env_1.pricing_date))
        val_env.add_constant('frequency', 'W')
        val_env.add_constant('paths', PortfolioRisk.PATHS)
        val_env.add_constant('starting_date', val_env.pricing_date)
        val_env.add_constant('final_date', val_env.pricing_date)
        val_env.add_curve('discount_curve', self.risk_factors)

        port = dx.derivatives_portfolio(
            name='portfolio',  # name
            positions=positions,  # derivatives positions
            val_env=val_env,  # valuation environment
            risk_factors=risk_factors,  # relevant risk factors
            correlations=False,  # correlation between risk factors
            parallel=False)  # parallel valuation
        return port

    def bump_price(self, p: derivatives_portfolio, percentage):
        """ updates the underliying market env. Will update referenced objects too
        Args:
            p:
            percentage:
        """
        p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].update(initial_value=self.initial_value * percentage)

    def bump_volatility(self, p: derivatives_portfolio, basis_point: float):
        """ updates the underliying market env. Will update referenced objects too
        Args:
            p:
            basis point:
        """
        vol = p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].volatility
        p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].update(volatility=max(abs(vol + basis_point), .001))

    def reset_portfolio(self, p: derivatives_portfolio):
        """ reset the portfolio to initial values
        Args:
            p:
        """
        p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].update(volatility=self.volatility)
        p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].update(initial_value=self.initial_value)

    def price_risk_report(self, p: derivatives_portfolio):
        for i in np.arange(.85, 1.15, .05):
            self.bump_price(p, i)
            print(f"initial underlying {p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].initial_value}")
            s = p.get_statistics()
            print(s)

    def volatility_risk_report(self, p: derivatives_portfolio):
        results = []
        for i in np.arange(-0.03, 0.03, .005):
            self.bump_volatility(p, i)
            print(f"initial volatility {p.underlying_objects[PortfolioRisk.UNDERLYING_GBM].volatility}")
            s = p.get_statistics()
            print(s)
            results.append(s)
            self.reset_portfolio(p)
        return results


if __name__ == '__main__':
    pr = PortfolioRisk(short_rate=0.01, initial_value=110.0, volatility=.18, pricing_date=dt.datetime(2020, 11, 23))
    positions = {
        'put_1': pr.define_position(quantity=1, strike=105.0, maturity=dt.datetime(2021, 6, 30), payoff='put'),
        'call_1': pr.define_position(quantity=2, strike=115.0, maturity=dt.datetime(2021, 6, 30), payoff='call'),
        'call_2': pr.define_position(quantity=-1, strike=120.0, maturity=dt.datetime(2021, 6, 30), payoff='call'),
        'put2': pr.define_position(quantity=1, strike=115.0, maturity=dt.datetime(2021, 6, 30), payoff='put')
    }
    res = pr.define_portfolio(positions)

    pr.volatility_risk_report(res)
    # pr.price_risk_report(res)
