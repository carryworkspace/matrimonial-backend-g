from app import app

# from app.routes import hotel
# app.register_blueprint(hotel)


if __name__ == "__main__":
    with app.app_context():
        pass
    app.run(debug=True)
