import os
import typing
from io import StringIO
from sqlalchemy import create_engine
import psycopg2
import psycopg2.extras as extras


class DBUtils:
    @staticmethod
    def connection(conf: typing.Dict):
        return psycopg2.connect(**conf)

    @staticmethod
    def sqlalchemy_engine(conf: typing.Dict):
        return create_engine(
            f"postgresql+psycopg2://{conf.get('user')}:{conf.get('password')}@{conf.get('host')}:{conf.get('port')}/{conf.get('database')}") # noqa

    @staticmethod
    def execute_many(conn, df, table):
        """
        Using cursor.executemany() to insert the dataframe
        """
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % (table, cols)
        cursor = conn.cursor()
        try:
            cursor.executemany(query, tuples)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("execute_many() done")
        cursor.close()

    @staticmethod
    def execute_batch(conn, df, table, page_size=100):
        """
        Using psycopg2.extras.execute_batch() to insert the dataframe
        """
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES(%%s,%%s,%%s)" % (table, cols)
        cursor = conn.cursor()
        try:
            extras.execute_batch(cursor, query, tuples, page_size)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("execute_batch() done")
        cursor.close()

    @staticmethod
    def execute_values(conn, df, table):
        """
        Using psycopg2.extras.execute_values() to insert the dataframe
        """
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
        cursor = conn.cursor()
        try:
            extras.execute_values(cursor, query, tuples)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("execute_values() done")
        cursor.close()

    @staticmethod
    def execute_mogrify(conn, df, table):
        """
        Using cursor.mogrify() to build the bulk insert query
        then cursor.execute() to execute the query
        """
        # Create a list of tuples from the dataframe values
        tuples = [tuple(x) for x in df.to_numpy()]
        # Comma-separated dataframe columns
        cols = ','.join(list(df.columns))
        # SQL query to execute
        cursor = conn.cursor()
        values = [cursor.mogrify("(%s,%s,%s)", tup).decode('utf8') for tup in tuples]
        query = "INSERT INTO %s(%s) VALUES " % (table, cols) + ",".join(values)

        try:
            cursor.execute(query, tuples)
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("execute_mogrify() done")
        cursor.close()

    @staticmethod
    def copy_from_file(conn, df, table):
        """
        Here we are going save the dataframe on disk as
        a csv file, load the csv file
        and use copy_from() to copy it to the table
        """
        # Save the dataframe to disk
        tmp_df = "./tmp_dataframe.csv"
        df.to_csv(tmp_df, index_label='id', header=False)
        f = open(tmp_df, 'r')
        cursor = conn.cursor()
        try:
            cursor.copy_from(f, table, sep=",")
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            os.remove(tmp_df)
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("copy_from_file() done")
        cursor.close()
        os.remove(tmp_df)

    @staticmethod
    def copy_from_stringio(conn, df, table):
        """
        Here we are going save the dataframe in memory
        and use copy_from() to copy it to the table
        """
        # save dataframe to an in memory buffer
        buffer = StringIO()
        df.to_csv(buffer, index_label='id', header=False)
        buffer.seek(0)

        cursor = conn.cursor()
        try:
            cursor.copy_from(buffer, table, sep=",")
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            cursor.close()
            return 1
        print("copy_from_stringio() done")
        cursor.close()
