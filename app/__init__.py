import os
from pathlib import Path
from flask import Flask
from flask import logging

from .db import db, RecordsModel
from settings import BASE_BATH


def create(dev_mode: bool = False):
    app = Flask(__name__, instance_relative_config=True)

    # Initialize DB
    db_name = '.db' if not dev_mode else 'debug.db'
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_BATH / db_name}"
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    logger = logging.create_logger(app)

    from . import records
    from . import graphics

    app.register_blueprint(records.bp)
    app.register_blueprint(graphics.bp)

    return app
