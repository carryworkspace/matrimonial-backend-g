from app import app
from app.extentions.logger import Logger

# from app.routes import hotel
# app.register_blueprint(hotel)


if __name__ == "__main__":
    Logger.setup_logger()
    with app.app_context():
        pass
    app.run(debug=True)
