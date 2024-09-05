import mysql.connector
from mysql.connector import pooling
from config import Config

class MySQLConnector:
    def __init__(self, database =Config.DB_NAME , user = Config.DB_USER, password  = Config.DB_PASSWORD, host=Config.DB_HOST, pool_name="mypool", pool_size=10):
        self.conn = None
        self.config = {
            'database': database,
            'user': user,
            'password': password,
            'host': host
        }
        self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            **self.config
        )

    def get_connection(self):
        """
        Acquire a connection from the pool.
        """
        try:
            self.conn = self.pool.get_connection()
            return self.conn
        except mysql.connector.Error as err:
            print(f"Error getting connection from pool: {err}")
            raise

    def close_connection(self):
        """
        Close the connection and return it to the pool.
        """
        if self.conn.is_connected():
            print("Closing connection")
            self.conn.close()

    def execute_query(self, query, params=None):
        """
        Execute a query and return the results.
        """
        
        cursor = self.conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                return result
            else:
                self.conn.commit()
                return cursor.rowcount
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
            raise
        finally:
            cursor.close()
        
    def close_pool(self):
        """
        Close the connection and return it to the pool.
        """       
        self.close_connection(self.conn)
