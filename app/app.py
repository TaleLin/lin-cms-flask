"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import Flask
from flask_cors import CORS
from lin import Lin


def register_blueprints(app):
    from app.api.v1 import create_v1
    from app.api.cms import create_cms
    app.register_blueprint(create_v1(), url_prefix='/v1')
    app.register_blueprint(create_cms(), url_prefix='/cms')


def apply_cors(app):
    CORS(app)


def create_tables(app):
    from lin.db import db
    with app.app_context():
        db.create_all()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.setting')
    app.config.from_object('app.config.secure')
    register_blueprints(app)
    Lin(app)
    apply_cors(app)
    # 创建所有表格
    create_tables(app)
    return app
