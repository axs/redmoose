import typing

import QuantLib as ql
import numpy as np
import pandas as pd


def volatility_surface(start_date: ql.Date, num_periods, strikes: range) -> ql.BlackVarianceSurface:
    """
    vs = volatility_surface(start_date: ql.Date, 24, range(10, 90, 10))
    vs.blackVol(today_date+4, 76.3)
    vs.blackForwardVol(today_date+4,today_date+9,73.3)
    Args:
        start_date:
        num_periods:
        strikes:

    Returns: BlackVarianceSurface
    """
    maturity = []
    for i in range(num_periods):
        maturity.append(start_date + ql.Period(i, ql.Months))
    vol = abs(np.random.randn(num_periods, len(strikes))).transpose().tolist()
    vol_surf = ql.BlackVarianceSurface(start_date - 1, ql.TARGET(), maturity, strikes, vol, ql.Actual365Fixed())
    return vol_surf


def volatility_curve(start_date: ql.Date, end_date: ql.Date, vols: typing.List[float]) -> ql.BlackVarianceCurve:
    """
    vt = volatility_curve(Date(15,2,2015), Date(20,2,2015),  [ 0.10, 0.12])
    vt.blackVol(Date(15,2,2015) +1, 23.3)
    Args:
        start_date:
        end_date:
        vols:

    Returns: BlackVarianceCurve
    """
    vt = ql.BlackVarianceCurve(start_date - 1,
                               [start_date, end_date],
                               vols,
                               ql.Thirty360())
    return vt


def normalize_vec(arr: typing.List):
    """
    http://blog.wolfire.com/2009/07/linear-algebra-for-game-developers-part-2/
    """
    return arr / np.linalg.norm(arr)


def entropy(*args):
    """
    args => AoA
    a = [0, 1, 1, 0, 1, 0, 0, 0, 1, 0] and b = [1, 1, 1, 0, 0, 0, 1, 0, 1, 0]
    """
    xy = zip(*args)
    # probs
    prob = [float(xy.count(c)) / len(xy) for c in dict.fromkeys(list(xy))]
    entropy = - sum([p * np.log2(p) for p in prob])
    return entropy


def convenienceYield(r, T, F, S):
    """ http://en.wikipedia.org/wiki/Convenience_yield
        inventories low -> S > F -> c > r   (backwardation)
        inventories high -> S < F -> c < r  (contango)
        r =.035
        T = .5  6month
        F = 1300.0
        S = 1371.0
    """
    recipT = 1 / float(T)
    return r + recipT * (1 - (F / S))


def convenienceYieldContinous(r, T, F, S):
    """
        r =.035
        T = .5  6month
        F = 1300.0
        S = 1371.0
    """
    recipT = 1 / float(T)
    return r - recipT * np.log(F / S)


def profitfactor(avgwinday, avglosday, numwindays, numlosdays):
    return avgwinday / avglosday * numwindays / numlosdays


def QuoteImbalance(sharesAddedBestbid, sharesCxlBestbid, sharesAddedBestask, sharesCxlBestask):
    return sharesAddedBestbid - sharesCxlBestbid - sharesAddedBestask + sharesCxlBestask


def TradeImbalance(sharesTradedAboveMid, SharesTradedBelowMid):
    return sharesTradedAboveMid - SharesTradedBelowMid


def moneyness(strike, price):
    return np.log(strike / price)


def beta(dfpctchg: pd.DataFrame, seriespctchg: pd.Series):
    """ dfpctchg : 2 column pctchange dataframe
        seriespctchg : series of second column

        In [32]: p.tail()
        Out[32]:
                    Adj_Close    Settle
        Date
        2014-12-09   0.002320  0.012182
        2014-12-10  -0.016204 -0.044076
        2014-12-11  -0.020392 -0.015860
        2014-12-12  -0.031225 -0.035056
        2014-12-15  -0.016529 -0.031336

        In [31]: p.cov() /  p.Settle.var()
        Out[31]:
                   Adj_Close    Settle
        Adj_Close   0.687536  0.479343
        Settle      0.479343  1.000000

        beta:   0.479343
    """
    return dfpctchg.cov() / seriespctchg.var()


def sharpe_ratio(mkt_rets):
    """
    Args:
        mkt_rets
    Returns:
        annualized sigma
        annualized mean
        sharpe ratio
    """
    mu, sigma = 12 * mkt_rets.mean(), np.sqrt(12 * mkt_rets.var())
    values = np.array([mu, sigma, mu / sigma]).squeeze()
    index = ["mu", "sigma", "SR"]
    return pd.Series(values, index=index)
