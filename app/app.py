"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import json
import time

from app.libs.lin_flask import LinFlask
from flask import request, g
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


def register_before_request(app):
    @app.before_request
    def request_cost_time():
        g.request_start_time = time.time()
        g.request_time = lambda: "%.5f" % (time.time() - g.request_start_time)


def register_after_request(app):
    @app.after_request
    def log_response(resp):
        log_config = app.config.get('LOG')
        if not log_config['REQUEST_LOG']:
            return resp
        message = '[%s] -> [%s] from:%s costs:%.3f ms' % (
            request.method,
            request.path,
            request.remote_addr,
            float(g.request_time()) * 1000
        )
        if log_config['LEVEL'] == 'INFO':
            app.logger.info(message)
        elif log_config['LEVEL'] == 'DEBUG':
            req_body = '{}'
            try:
                req_body = request.get_json() if request.get_json() else {}
            except:
                pass
            message += " data:{\n\tparam: %s, \n\tbody: %s\n} " % (
                json.dumps(request.args, ensure_ascii=False),
                req_body
            )
            app.logger.debug(message)
        return resp


def create_app(register_all=True, environment='production'):
    app = LinFlask(__name__, static_folder='./assets')
    app.config['ENV'] = environment
    env = app.config.get('ENV')
    if env == 'production':
        app.config.from_object('app.config.setting.ProductionConfig')
        app.config.from_object('app.config.secure.ProductionSecure')
    elif env == 'development':
        app.config.from_object('app.config.setting.DevelopmentConfig')
        app.config.from_object('app.config.secure.DevelopmentSecure')
    app.config.from_object('app.config.log')
    if register_all:
        register_blueprints(app)
        Lin(app)
        register_before_request(app)
        register_after_request(app)
        apply_cors(app)
        # 创建所有表格
        create_tables(app)

    return app
