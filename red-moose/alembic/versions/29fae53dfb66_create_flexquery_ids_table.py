"""create flexquery IDs table

Revision ID: 29fae53dfb66
Revises: 7bc857c79ef6
Create Date: 2020-10-06 08:21:48.706593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '29fae53dfb66'
down_revision = '7bc857c79ef6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
            'flex_query',
            sa.Column('flex_id', sa.Integer, autoincrement=True, primary_key=True),
            sa.Column('token', sa.Numeric, nullable=False),
            sa.Column('query_id', sa.Integer, nullable=False),
            sa.Column('is_active', sa.Boolean,nullable=False, server_default=sa.text(u"TRUE")),
            sa.Column('modified', sa.TIMESTAMP(timezone=True),
                      server_default=sa.text(u"TIMEZONE('utc', CURRENT_TIMESTAMP)"), nullable=False),
        )
    with op.get_context().autocommit_block():
        try:
            role = "CREATE ROLE redmoose with LOGIN ENCRYPTED PASSWORD 'redmoose'"
            op.execute(role)
        except Exception as e:
            pass
    grant="GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO redmoose"
    op.execute(grant)
    sequ="GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO redmoose"
    op.execute(sequ)
    func="GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO redmoose"
    op.execute(func)

def downgrade():
    op.drop_table('flex_query')
