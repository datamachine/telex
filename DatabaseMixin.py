import sqlite3
from enum import Enum
import logging


class DatabaseMixin():
    def __init__(self):
        self.table_name = self.__class__.__name__
        if not hasattr(self, "schema"):
            raise DatabaseError("Missing Schema in plugin {0}".format(self.table_name))

        self.conn = sqlite3.connect('data/data.db')
        self.conn.row_factory = DatabaseMixin.dict_factory
        self.create_schema()

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def create_schema(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (self.table_name,))
            if cur.fetchone() is None:
                logging.debug("Initializing schema for {0}".format(self.table_name))

                columns = ", ".join(["{0} {1}".format(col, dbtype.value) for col, dbtype in self.schema.items()])
                sql = "CREATE TABLE {0}( {1} );".format(self.table_name, columns)
                logging.debug(sql)
                self.conn.execute(sql)
        except sqlite3.Error as e:
            logging.error("Error creating table for {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def insert(self, **kwargs):
        try:
            cur = self.conn.cursor()
            sql = "INSERT INTO {table} ({columns}) VALUES ('{values}')".format(
                table=self.table_name,
                columns=", ".join(kwargs.keys()),
                values="', '".join([str(kwargs[col]) for col in kwargs.keys()])
            )
            #logging.debug(sql)
            cur.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            logging.error("Error inserting into {0}: {1}".format(self.table_name, e.args[0]))
        finally:
            cur.close()

    def select(self, **kwargs):
        try:
            cur = self.conn.cursor()
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

    def query(self, sql):
        try:
            cur = self.conn.cursor()
            #logging.debug(sql)
            cur.execute(sql)
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
    Integer = "INT"
    Real = Float = Double = "REAL"
    String = "TEXT"
    DateTime = "DATETIME"
    Blob = Binary = "BLOB"