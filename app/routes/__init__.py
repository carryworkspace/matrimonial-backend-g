from flask import Blueprint, g
from mysql import connector
from config import Config
import mysql.connector.pooling as pooling
from app.extentions.logger import Logger
from mysql.connector.cursor import MySQLCursorAbstract
from app.database.database import Database as _database
from app.database.db_pooling import MySQLConnector
# db = None
# cursorDb = None
Router = Blueprint('Router', __name__)

# conn = MySQLConnector()
# _database = Database()
# Router = Blueprint('Router', __name__, url_prefix='/v1')
# db_pool: connector.connection.MySQLConnection = None


# def createNormalDbConnection():
#     # global db, cursorDb

#     print("********************",Config.DB_HOST, Config.DB_USER, Config.DB_PASSWORD, Config.DB_NAME    )
#     db = connector.connect(
#         host=Config.DB_HOST,
#         user=Config.DB_USER,
#         password=Config.DB_PASSWORD,
#         database=Config.DB_NAME
#     )
    
#     cursorDb = db.cursor(dictionary=True)
#     if db.get_server_info() is not None:
#         print("Database connected")
#     return db, cursorDb

# def createDbConnection():
#     global db, cursorDb

#     if db is None:
#         db = connector.connect(
#             host=Config.DB_HOST,
#             user=Config.DB_USER,
#             password=Config.DB_PASSWORD,
#             database=Config.DB_NAME
#         )
#         print("Database connected")
#         try:
#             db_connect = db.get_server_info()
#             cursorDb = db.cursor(dictionary=True)
#         except:
#             Logger.error("Error in connection")
#             Logger.warning("Retrying connection")
#             db = connector.connect(
#                 host=Config.DB_HOST,
#                 user=Config.DB_USER,
#                 password=Config.DB_PASSWORD,
#                 database=Config.DB_NAME
#             )
#             print("Database connected")
        
            

#     return db, cursorDb

# def createDbConnectionPool():
#     global db_pool

#     if db_pool is None:
#         # Create a connection pool
#         db_pool = pooling.MySQLConnectionPool(
#             pool_name="mypool",
#             pool_size=10,  # Adjust the pool size as needed
#             pool_reset_session=True,
#             host=Config.DB_HOST,
#             user=Config.DB_USER,
#             password=Config.DB_PASSWORD,
#             database=Config.DB_NAME
#         )
#         print("Connection pool created")

#     try:
#         db = db_pool.get_connection()
#         cursorDb = db.cursor(dictionary=True)
#     except:
#         Logger.error("Error in connection")
#         Logger.warning("Retrying connection")
        
#         db_pool = pooling.MySQLConnectionPool(
#             pool_name="mypool",
#             pool_size=10,  # Adjust the pool size as needed
#             pool_reset_session=True,
#             host=Config.DB_HOST,
#             user=Config.DB_USER,
#             password=Config.DB_PASSWORD,
#             database=Config.DB_NAME
#         )
#         db = db_pool.get_connection()
#         cursorDb = db.cursor(dictionary=True)
#         print("Connection pool created")
        
#     # Get a connection from the pool
    
#     # Create a cursor

#     if db.is_connected():
#         print("Database connected from pool")

#     return db, cursorDb

def closeDbConnection(db, cursorDb):
    db.close()
    cursorDb.close()
    print("Database Disconnected")

def closePoolConnection(db):
    db.close()
    print("Database Disconnected from pool")


from .user import user_routes
from .profile import profile_routes
from .match_making import match_making_routes
from .data import data_routes
