from flask import Blueprint, g
from mysql import connector
from config import Config

# db = None
# cursorDb = None
Router = Blueprint('Router', __name__)

def createDbConnection():
    # global db, cursorDb

    db = connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
    cursorDb = db.cursor(dictionary=True)
    if db.get_server_info() is not None:
        print("Database connected")
    return db, cursorDb

def closeDbConnection(db, cursorDb):
    # db.close()
    cursorDb.close()
    print("Database Disconnected")


# from . import hotel  

from .user import user_routes
from .profile import profile_routes
from .match_making import match_making_routes
