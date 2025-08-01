import sys, psycopg2, psycopg2.sql as sql
from dotenv import load_dotenv
load_dotenv()


from psycopg2 import pool


class Database():
    """
    the connection_pool is a static property of the Database Class
    """
    __connection_pool = None

    @classmethod
    def initialise(cls, **kwargs):
        cls.__connection_pool = pool.SimpleConnectionPool(1, 10, **kwargs)

    @classmethod
    def get_connection(cls):
        return cls.__connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        Database.__connection_pool.putconn(connection)


    @classmethod
    def delete_all_connections(cls):
        Database.__connection_pool.closeall()

class CurserFromConnectionFromPool():
    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection= Database.get_connection()
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_value is not None:
            self.connection.rollback()
        else:
            self.cursor.close()
            self.connection.commit()
            Database.return_connection(self.connection)
