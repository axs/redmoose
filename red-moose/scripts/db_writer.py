import pypath
from red_moose.persistence.persist import DBPositionWriter
from red_moose.ib.client import IBClient
from red_moose.common import AppContext
import datetime

app = AppContext()
app.street_trade_date = datetime.datetime.utcnow()
ib = IBClient()
p = DBPositionWriter.from_config()

p.write(ib.portfolio())
