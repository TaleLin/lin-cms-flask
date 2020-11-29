"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""


from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.lin import Lin


def register_blueprints(app):
    from app.api.cms import create_cms
    from app.api.v1 import create_v1

    app.register_blueprint(create_v1(), url_prefix="/v1")
    app.register_blueprint(create_cms(), url_prefix="/cms")


def apply_cors(app):
    CORS(app)


def load_config(app):
    """
    根据指定配置环境自动加载对应环境变量和配置类
    """
    # 兼容 其他HTTP Server托管启动, 手动读取环境配置
    load_dotenv(".flaskenv")
    # 根据传入环境加载对应配置
    env = app.config.get("ENV")
    # 读取 .env
    load_dotenv(".{env}.env".format(env=env))
    # 读取配置类
    app.config.from_object(
        "app.config.{env}.{Env}Config".format(env=env, Env=env.capitalize())
    )
    # 加载 code message
    app.config.from_object("app.config.codemsg")


def create_app(register_all=True, **kwargs):
    app = Flask(__name__, static_folder="./assets")
    load_config(app)
    if register_all:
        register_blueprints(app)
        Lin(app, **kwargs)
        apply_cors(app)
    return app
