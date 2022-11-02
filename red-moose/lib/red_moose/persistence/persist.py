import abc
import logging
from typing import List, Union, Iterator

import attr
import ib_insync
import pandas as pd
import numpy as np
import psycopg2
import psycopg2.extras as extras
import sqlalchemy as sa
from ib_insync.flexreport import FlexReport

from red_moose.common import AppContext, Position, Bar
from red_moose.rm_enums import WriterType, FlexQueryType, IQFeedIntervalType
from red_moose.rm_types import PersistentRecord

log = logging.getLogger(__name__)


class Writer(abc.ABC):

    @abc.abstractmethod
    def write(self, record: Union[List[PersistentRecord], pd.DataFrame, Iterator[Bar]]):
        pass

    @staticmethod
    def factory(writer_type: WriterType, **kwargs):
        dispatch = {writer_type.POSTGRES: DBPositionWriter,
                    writer_type.PARQUET: ParquetPositionWriter,
                    writer_type.FLEX: FlexQueryResultsWriter}
        return dispatch[writer_type](**kwargs)


class DBPositionWriter(Writer):
    def __init__(self, **kwargs):
        self.db_conn = kwargs.get('db_connection')

    @classmethod
    def from_config(cls):
        return cls(db_connection=AppContext().db_connection)

    def write(self, records: List[PersistentRecord]):
        log.info(records)
        columns = ",".join([f.name for f in attr.fields(Position)])
        query = f"""INSERT INTO
                positions_rt({columns})
                VALUES %s"""
        log.info(query)
        cursor = self.db_conn.cursor()
        try:
            extras.execute_values(cursor, query, [attr.astuple(r) for r in records])
            self.db_conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            self.db_conn.rollback()
            cursor.close()
            return 1
        log.info("execute_values() done")
        cursor.close()


class ParquetPositionWriter(Writer):
    def __init__(self, **kwargs):
        self.destination = kwargs.get('destination_filename')

    def write(self, records: List[PersistentRecord]):
        log.info(f"Writing {len(records)} PortfolioItem records")

        existing_df = None
        try:
            existing_df = pd.read_parquet(f"{self.destination}.gzip")
        except FileNotFoundError as e:
            log.exception(e)

        portfolio_df = ib_insync.util.df(records)
        contract_df = ib_insync.util.df(portfolio_df.contract.tolist())
        portfolio_df.drop(columns=['contract'], inplace=True)
        df = pd.concat([portfolio_df, contract_df], axis=1)
        df['timestamp'] = pd.Timestamp('now', tz='UTC', unit='s')

        if existing_df is not None:
            df = pd.concat([existing_df, df], axis=0)

        log.debug(df.tail(1).T)
        log.info(f"writing positions to {self.destination}.gzip")
        df.to_parquet(f"{self.destination}.gzip", compression='gzip', allow_truncated_timestamps=True)


class IQFeedBarWriter(Writer):
    def __init__(self, **kwargs):
        self.destination = kwargs.get('destination_filename')
        self.iq_client = kwargs.get('iq_client')

    def get_bars(self, ticker, bar_len, num_bars) -> Iterator[Bar]:
        """
        bar_data = i.get_historical_bar_data('AAPL', 60, IQFeedIntervalType.SECONDS.value, 20)
        Args:
            ticker:
            bar_len: in seconds
            num_bars:

        Returns:
        """
        q = None
        bar_data = self.iq_client.get_historical_bar_data(ticker, bar_len, IQFeedIntervalType.SECONDS.value, num_bars)
        for bar in bar_data:
            try:
                q = Bar(
                    Symbol=ticker,
                    Date=bar[0],
                    Time=bar[1],
                    Open=bar[2],
                    High=bar[3],
                    Low=bar[4],
                    Close=bar[5],
                    TotalVolume=bar[6],
                    PeriodVolume=bar[7],
                    NumTrades=bar[8]
                )
            except Exception as e:
                log.exception(e)
            yield q

    def write(self, records: List[PersistentRecord]):
        log.info(f"Writing {len(records)} Bar records")
        for bar in records:
            print(bar)


class FlexQueryResultsWriter(Writer):
    def __init__(self, **kwargs):
        # token='15263501289750279079293'
        # queryid=445592
        queryId = kwargs.get('queryId')
        token = kwargs.get('token')
        self.flex_type: FlexQueryType = kwargs.get('flex_query_type')
        self.flex_report = FlexReport(token=token, queryId=queryId)

    def get_flex_results(self):
        if self.flex_type == FlexQueryType.TRANSACTIONS:
            return self.flex_report.df('Trade')
        elif self.flex_type == FlexQueryType.POSITIONS:
            return self.flex_report.df('OpenPosition')

    def write(self, record: pd.DataFrame):
        self._write(record, self.flex_type.value)

    def _write(self, record: pd.DataFrame, table: str):
        record.columns = record.columns.str.lower()
        meta_data = sa.MetaData(bind=AppContext().sqlalchemy_engine, reflect=True)
        table_obj = meta_data.tables[table]
        columns = [c.name for c in table_obj.columns if c.name not in {'txn_id', 'pos_id'}]
        record = record.replace(r'^\s*$', np.nan, regex=True)
        log.info(f"writing {columns} to {table}")
        record[columns].to_sql(table,
                               AppContext().sqlalchemy_engine,
                               index=False,
                               if_exists='append',
                               chunksize=5000)
