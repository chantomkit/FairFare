from flask import Flask


def create_app():
    app = Flask(__name__)

    # Register routes from routes.py
    from .routes import register_routes

    register_routes(app)

    return app
