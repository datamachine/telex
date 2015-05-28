import sqlite3
from enum import Enum
import logging


class DatabaseMixin():
    def __init__(self):
        self.table_name = self.__class__.__name__
        if not hasattr(self, "schema"):
            raise DatabaseError("Missing Schema in plugin {0}".format(self.table_name))

        self.create_schema()

    def get_conn(self):
        conn = sqlite3.connect('data/data.sqlite')
        conn.row_factory = DatabaseMixin.dict_factory
        return conn

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_schema(self):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.table_name,))
            if cur.fetchone() is None:
                logging.debug("Initializing schema for {0}".format(self.table_name))
                columns = []
                for col, dbtype in self.schema.items():
                    pkey = ""
                    if hasattr(self, 'primary_key') and col == self.primary_key:
                        pkey = "PRIMARY KEY"

                    columns.append("{0} {1} {2}".format(col, dbtype.value, pkey))

                sql = "CREATE TABLE {0}( {1} );".format(self.table_name, ", ".join(columns))
                logging.debug(sql)
                conn.execute(sql)
        except sqlite3.Error as e:
            logging.error("Error creating table for {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def insert(self, **kwargs):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            columns = kwargs.keys()
            parameters = ",".join(["?"] * len(columns))
            values = [str(v) for v in kwargs.values()]

            # TODO: Ignore pkey collision, may want to update instead
            sql = "INSERT OR IGNORE INTO {table} ({columns}) VALUES ({values})".format(
                table=self.table_name,
                columns=", ".join(columns),
                values=parameters
            )
            cur.execute(sql, values)
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Error inserting into {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def insert_many(self, columns, values):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            parameters = ",".join(["?"] * len(columns))

            sql = "INSERT OR IGNORE INTO {table} ({columns}) VALUES ({values})".format(
                table=self.table_name,
                columns=", ".join(columns),
                values=parameters
            )
            #logging.debug(sql)
            cur.executemany(sql, values)
            conn.commit()
        except sqlite3.Error as e:
            logging.error("Error inserting into {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def select(self, **kwargs):
        try:
            self.get_conn()
            cur = conn.cursor()
            sql = "SELECT  {columns} FROM {table} WHERE 1 {values}".format(
                table=self.table_name,
                columns=", ".join(kwargs.keys()),
                values=" AND ".join(["{0} = '{1}'".format(col, str(kwargs[col])) for col in kwargs.keys()])
            )
            #logging.debug(sql)
            cur.execute(sql)
            return cur.fetchall()
        except sqlite3.Error as e:
            logging.error("Error selecting table {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def query(self, sql, parameters=None):
        try:
            conn = self.get_conn()
            cur = conn.cursor()
            #logging.debug(sql)
            if parameters:
                cur.execute(sql, parameters)
            else:
                cur.execute(sql)
            conn.commit()
            return cur.fetchall()
        except sqlite3.Error as e:
            logging.error("Error selecting table {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def __del__(self):
        pass

class DatabaseError(Exception):
    pass


class DbType(Enum):
    Integer = "INTEGER"
    Real = Float = Double = "REAL"
    String = "TEXT"
    DateTime = "DATETIME"
    Blob = Binary = "BLOB"
