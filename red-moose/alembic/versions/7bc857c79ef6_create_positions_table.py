"""create positions table

Revision ID: 7bc857c79ef6
Revises: 
Create Date: 2020-08-27 11:41:11.205609

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7bc857c79ef6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'positions_rt',
        sa.Column('position_id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('account', sa.String(32), nullable=False),
        sa.Column('quantity', sa.DECIMAL(), nullable=False),
        sa.Column('sec_type', sa.String(16), nullable=False),
        sa.Column('sec_id_type', sa.String(16), nullable=False),
        sa.Column('contract_id', sa.Integer, nullable=False),
        sa.Column('sec_id', sa.String(32), nullable=False),
        sa.Column('avg_cost', sa.DECIMAL(), nullable=False),
        sa.Column('market_value', sa.DECIMAL(), nullable=True),
        sa.Column('realized_pnl', sa.DECIMAL(), nullable=True),
        sa.Column('unrealized_pnl', sa.DECIMAL(), nullable=True),
        sa.Column('market_price', sa.DECIMAL(), nullable=True),
        sa.Column('street_trade_date', sa.DATE, nullable=False),
        sa.Column('modified', sa.TIMESTAMP(timezone=True),
                  server_default=sa.text(u"TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
    )

    op.create_table(
        'transactions',
        sa.Column('txn_id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('accountid', sa.String(32), nullable=False),
        sa.Column('currency', sa.String(8), nullable=True),
        sa.Column('assetcategory', sa.String(16), nullable=True),
        sa.Column('symbol', sa.String(32), nullable=True),
        sa.Column('conid', sa.BigInteger, nullable=False),
        sa.Column('datetime', sa.String(16), nullable=False),
        sa.Column('tradedate', sa.Integer, nullable=False),
        sa.Column('settledatetarget', sa.Integer, nullable=False),
        sa.Column('underlyingsymbol', sa.String(32), nullable=True),
        sa.Column('underlyingconid', sa.BigInteger, nullable=True),
        sa.Column('ordertime', sa.String(16), nullable=True),
        sa.Column('opencloseindicator', sa.String(8), nullable=True),
        
        sa.Column('transactiontype', sa.String(16), nullable=True),
        sa.Column('exchange', sa.String(16), nullable=True),

        sa.Column('quantity', sa.DECIMAL(), nullable=True),

        sa.Column('tradeprice', sa.DECIMAL(), nullable=True),
        sa.Column('trademoney', sa.DECIMAL(), nullable=True),
        sa.Column('taxes', sa.DECIMAL(), nullable=True),
        sa.Column('ibcommission', sa.DECIMAL(), nullable=True),
        sa.Column('ibcommissioncurrency', sa.String(8), nullable=True),
        sa.Column('netcash', sa.DECIMAL(), nullable=True),
        sa.Column('closeprice', sa.DECIMAL(), nullable=True),

        sa.Column('transactionid', sa.BigInteger, nullable=False),
        sa.Column('buysell', sa.String(8), nullable=True),
        sa.Column('iborderid', sa.BigInteger, nullable=False),
        sa.Column('ibexecid', sa.String(32), nullable=True),
        sa.Column('brokerageorderid', sa.String(32), nullable=True),
        sa.Column('levelofdetail', sa.String(16), nullable=True),

        sa.Column('changeinprice', sa.DECIMAL(), nullable=True),
        sa.Column('changeinquantity', sa.DECIMAL(), nullable=True),
        sa.Column('ordertype', sa.String(16), nullable=True),
        sa.Column('traderid', sa.String(16), nullable=True),
        sa.Column('isapiorder', sa.String(8), nullable=True)
    )

    op.create_table(
        'positions',
        sa.Column('pos_id', sa.Integer, autoincrement=True, primary_key=True),
        sa.Column('accountid', sa.String(32), nullable=False),
        sa.Column('currency', sa.String(8), nullable=True),
        sa.Column('assetcategory', sa.String(32), nullable=True),
        sa.Column('symbol', sa.String(32), nullable=True),
        sa.Column('underlyingsymbol', sa.String(32), nullable=True),
        sa.Column('conid', sa.BigInteger, nullable=False),
        sa.Column('underlyingconid', sa.BigInteger, nullable=True),

        sa.Column('reportdate', sa.String(8), nullable=True),
        sa.Column('strike', sa.DECIMAL(), nullable=True),
        sa.Column('expiry', sa.Integer, nullable=True),
        sa.Column('putcall', sa.String(8), nullable=True),
        sa.Column('listingexchange', sa.String(32), nullable=True),

        sa.Column('position', sa.DECIMAL(), nullable=True),

        sa.Column('markprice', sa.DECIMAL(), nullable=True),
        sa.Column('positionvalue', sa.DECIMAL(), nullable=True),
        sa.Column('openprice', sa.DECIMAL(), nullable=True),
        sa.Column('costbasisprice', sa.DECIMAL(), nullable=True),
        sa.Column('costbasismoney', sa.String(32), nullable=True),
        sa.Column('percentofnav', sa.DECIMAL(), nullable=True),
        sa.Column('fifopnlunrealized', sa.DECIMAL(), nullable=True),
        sa.Column('side', sa.String(8), nullable=True)
    )

    with op.get_context().autocommit_block():
        try:
            role = "CREATE ROLE redmoose with LOGIN ENCRYPTED PASSWORD 'redmoose'"
            op.execute(role)
        except Exception as e:
            pass
    grant = "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO redmoose"
    op.execute(grant)
    sequ = "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO redmoose"
    op.execute(sequ)
    func = "GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO redmoose"
    op.execute(func)


def downgrade():
    op.drop_table('positions')
