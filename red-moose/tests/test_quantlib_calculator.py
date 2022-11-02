import pypath
from red_moose.modeling.quantlib_calculator import OptionArgs, OptionProfile, OptionCombinator
import QuantLib as ql


class TestCalculator:
    @classmethod
    def setup_class(cls):
        cls.start = 127
        cls.stop = 135
        cls.periods = 10
        cls.settle = ql.Date(13, ql.November, 2020)
        cls.expiry = ql.Date(23, ql.December, 2020)

    def test_under(self):
        df = OptionProfile.underlying_range(
            OptionArgs(
                underlying=ql.SimpleQuote(123.0),
                irate=ql.SimpleQuote(1.5 / 100.),
                sigma=ql.SimpleQuote(.12),
                settle=self.settle,
                expiry=self.expiry,
                strike=130.0,
                quantity=7,
                opttype=ql.Option.Call),
            self.start,
            self.stop,
            self.periods
        )
        print(df)

    def test_sigma(self):
        df = OptionProfile.sigma_range(
            OptionArgs(
                underlying=ql.SimpleQuote(123.0),
                irate=ql.SimpleQuote(1.5 / 100.),
                sigma=ql.SimpleQuote(2 / 100.),
                settle=self.settle,
                expiry=self.expiry,
                strike=130.0,
                quantity=2,
                opttype=ql.Option.Call),
            14,
            22,
            10
        )
        print(df)

    def test_daterange(self):
        df = OptionProfile.date_range(
            OptionArgs(
                underlying=ql.SimpleQuote(123.0),
                irate=ql.SimpleQuote(1.5 / 100.),
                sigma=ql.SimpleQuote(2 / 100.),
                settle=self.settle,
                expiry=self.expiry,
                strike=130.0,
                quantity=-2,
                opttype=ql.Option.Call)
        )
        print(df)


    def test_combinator(self):
        # straddle
        dfc = OptionProfile.date_range(
            OptionArgs(
                underlying=ql.SimpleQuote(130.0),
                irate=ql.SimpleQuote(1.5 / 100.),
                sigma=ql.SimpleQuote(2 / 100.),
                settle=self.settle,
                expiry=self.expiry,
                strike=130.0,
                quantity=1,
                opttype=ql.Option.Call)
        )
        dfp = OptionProfile.date_range(
                    OptionArgs(
                        underlying=ql.SimpleQuote(130.0),
                        irate=ql.SimpleQuote(1.5 / 100.),
                        sigma=ql.SimpleQuote(2 / 100.),
                        settle=self.settle,
                        expiry=self.expiry,
                        strike=130.0,
                        quantity=1,
                        opttype=ql.Option.Put)
                )

        oc = OptionCombinator.create_settle([dfc,dfp])
        df = oc.combine()
        print(df)
