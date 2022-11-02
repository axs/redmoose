from red_moose.common import AppContext


class Queries:

    @staticmethod
    def position_pnl(account_id, **kwargs):
        ctx = AppContext()
        cursor = ctx.db_connection.cursor()
        with_history = kwargs.get('history')
        reportdate_condition = (
            '1=1'
            if with_history
            else f"reportdate = (select max(reportdate) from positions where accountid='{account_id}')"
        )
        cursor.execute(f"""select coalesce(underlyingsymbol,symbol) symbolfamily,reportdate,assetcategory, sum(fifopnlunrealized) pnl
                          from positions where accountid = '{account_id}'
                          and {reportdate_condition}
                          group by 1,2,3
                          order by symbolfamily,reportdate""")
        rows = cursor.fetchall()
        return rows
