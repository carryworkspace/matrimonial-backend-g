from flask import Blueprint, g
from mysql import connector
from config import Config
import mysql.connector.pooling as pooling
from app.extentions.logger import Logger
from mysql.connector.cursor import MySQLCursorAbstract
from mysql.connector.abstracts import MySQLConnectionAbstract

    
conn = None
cursor = None

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
        self.connect()
    
    @staticmethod
    def get_connection():
        global conn, cursor
        try:
            if conn is None or not conn.is_connected():
                Logger.info("Reconnecting to the database...")
                _db = Database()
                conn = _db.conn
                cursor = _db.cursor
                Logger.info("Database reconnected")
        except Exception as e:
            Logger.error(f"Reconnection failed: {e}")
        return conn, cursor
    
    def connect(self):
        global conn, cursor
        """Establish a new connection to the database."""
        try:
            self.conn = connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
            )
            self.cursor = self.conn.cursor(dictionary=True)
            Logger.info("Database connected")
            conn = self.conn
            cursor = self.cursor
        except Exception as e:
            Logger.error(f"Error connecting to the database: {e}")

    def reconnect(self):
        """Reconnect to the database if the connection is lost."""
        try:
            if self.conn is None or not self.conn.is_connected():
                Logger.info("Reconnecting to the database...")
                self.connect()
        except Exception as e:
            Logger.error(f"Reconnection failed: {e}")
            
    def closeDbConnection(db, cursorDb):
        # db.close()
        cursorDb.close()
        print("Database Disconnected")

    def closePoolConnection(db):
        db.close()
        print("Database Disconnected from pool")