from flask import Flask
from app.routes import Router
from flask_cors import CORS
from mysql import connector
from config import Config
from .extentions.logger import Logger

Logger.setup_logger()
app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes

app.register_blueprint(Router)
# cache = Cache(app, config={'CACHE_TYPE': 'simple'})

if __name__ == "__main__":
    app.run(debug=True)
