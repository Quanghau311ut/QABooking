import os

from flask import Flask

from app.controllers.booking_controller import bookings


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "change-this-secret-key"),
        DEBUG=os.getenv("FLASK_DEBUG", "false").lower() == "true",
    )
    app.register_blueprint(bookings)
    return app
