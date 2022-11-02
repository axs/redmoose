import pypath
from red_moose.persistence.persist import DBPositionWriter
from red_moose.common import Position
import datetime
import pytest


class TestDBWrite:

    @classmethod
    def setup_class(cls):
        cls.p = DBPositionWriter.from_config()

    @classmethod
    def teardown_class(cls):
        cursor = cls.p.db_conn.cursor()
        cursor.execute('delete from positions where contract_id=666')

    @pytest.mark.skip('skipping when run in gitlab')
    def test_position_write(self):
        positions = [Position(account='DU230011', quantity=-5.0, sec_type='FUT', sec_id_type='', contract_id=666,
                              sec_id='',
                              avg_cost=42865.63, market_value=-214300.0, realized_pnl=50.52, unrealized_pnl=28.15,
                              market_price=42.8600006,
                              street_trade_date=datetime.datetime(2020, 8, 31, 23, 26, 23, 277303)),
                     ]

        self.p.write(positions)
