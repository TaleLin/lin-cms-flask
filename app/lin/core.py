"""
     core module of Lin.
     ~~~~~~~~~

     manager and main db models.

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from collections import namedtuple
from datetime import datetime, date

from flask import Flask, current_app, request, Blueprint
from flask.json import JSONEncoder as _JSONEncoder
from werkzeug.exceptions import HTTPException
from werkzeug.local import LocalProxy

from .logger import LinLog
from .db import db
from .jwt import jwt
from .exception import APIException, UnknownException, AuthFailed
from .interface import UserInterface, GroupInterface, AuthInterface,\
    LogInterface, EventInterface, FileInterface
from .exception import NotFound, ParameterException
from .config import Config

__version__ = '0.1.2'

# 路由函数的权限和模块信息(meta信息)
Meta = namedtuple('meta', ['auth', 'module'])

#       -> endpoint -> func
# auth                      -> module
#       -> endpoint -> func

# 记录路由函数的权限和模块信息
route_meta_infos = {}

# config for Lin plugins
# we always access config by flask, but it dependents on the flask context
# so we move the plugin config here,which you can access config more convenience

lin_config = Config()


def route_meta(auth, module='common', mount=True):
    """
    记录路由函数的信息
    记录路由函数访问的推送信息模板
    注：只有使用了 route_meta 装饰器的函数才会被记录到权限管理的map中
    :param auth: 权限
    :param module: 所属模块
    :param mount: 是否挂在到权限中（一些视图函数需要说明，或暂时决定不挂在到权限中，则设置为False）
    :return:
    """

    def wrapper(func):
        if mount:
            name = func.__name__ + str(func.__hash__())
            existed = route_meta_infos.get(name, None) and route_meta_infos.get(name).module == module
            if existed:
                raise Exception("func's name cant't be repeat in a same module")
            else:
                route_meta_infos.setdefault(name, Meta(auth, module))
        return func

    return wrapper


def find_user(**kwargs):
    return manager.find_user(**kwargs)


def find_group(**kwargs):
    return manager.find_group(**kwargs)


def get_ep_infos():
    """ 返回权限管理中的所有视图函数的信息，包含它所属module """
    infos = {}
    for ep, meta in manager.ep_meta.items():
        mod = infos.get(meta.module, None)
        if mod:
            sub = mod.get(meta.auth, None)
            if sub:
                sub.append(ep)
            else:
                mod[meta.auth] = [ep]
        else:
            infos.setdefault(meta.module, {meta.auth: [ep]})

    return infos


def find_info_by_ep(ep):
    """ 通过请求的endpoint寻找路由函数的meta信息"""
    return manager.ep_meta.get(ep)


def is_user_allowed(group_id):
    """查看当前user有无权限访问该路由函数"""
    ep = request.endpoint
    # 根据 endpoint 查找 authority
    meta = manager.ep_meta.get(ep)
    return manager.verity_user_in_group(group_id, meta.auth, meta.module)


def find_auth_module(auth):
    """ 通过权限寻找meta信息"""
    for _, meta in manager.ep_meta.items():
        if meta.auth == auth:
            return meta
    return None


class Lin(object):

    def __init__(self,
                 app: Flask = None,  # flask app , default None
                 group_model=None,  # group model, default None
                 user_model=None,  # user model, default None
                 auth_model=None,  # authority model, default None
                 create_all=False,  # 是否创建所有数据库表, default false
                 mount=True,  # 是否挂载默认的蓝图, default True
                 handle=True,  # 是否使用全局异常处理, default True
                 json_encoder=True,  # 是否使用自定义的json_encoder , default True
                 logger=True,   # 是否使用自定义系统日志，default True
                 ):
        self.app = app
        self.manager = None
        if app is not None:
            self.init_app(app, group_model, user_model, auth_model, create_all, mount, handle, json_encoder, logger)

    def init_app(self,
                 app: Flask,
                 group_model=None,
                 user_model=None,
                 auth_model=None,
                 create_all=False,
                 mount=True,
                 handle=True,
                 json_encoder=True,
                 logger=True
                 ):
        # default config
        app.config.setdefault('PLUGIN_PATH', {})
        # 默认蓝图的前缀
        app.config.setdefault('BP_URL_PREFIX', '/plugin')
        # 默认文件上传配置
        app.config.setdefault('FILE', {
            "STORE_DIR": 'app/assets',
            "SINGLE_LIMIT": 1024 * 1024 * 2,
            "TOTAL_LIMIT": 1024 * 1024 * 20,
            "NUMS": 10,
            "INCLUDE": set(['jpg', 'png', 'jpeg']),
            "EXCLUDE": set([])
        })
        json_encoder and self._enable_json_encoder(app)
        self.app = app
        # 初始化 manager
        self.manager = Manager(app.config.get('PLUGIN_PATH'),
                               group_model,
                               user_model,
                               auth_model)
        self.app.extensions['manager'] = self.manager
        db.init_app(app)
        create_all and self._enable_create_all(app)
        jwt.init_app(app)
        mount and self.mount(app)
        handle and self.handle_error(app)
        logger and LinLog(app)

    def mount(self, app):
        # 加载默认插件路由
        bp = Blueprint('plugin', __name__)
        # 加载插件的路由
        for plugin in self.manager.plugins.values():
            if len(plugin.controllers.values()) > 1:
                for controller in plugin.controllers.values():
                    controller.register(bp, url_prefix='/' + plugin.name)
            else:
                for controller in plugin.controllers.values():
                    controller.register(bp)
        app.register_blueprint(bp, url_prefix=app.config.get('BP_URL_PREFIX'))
        for ep, func in app.view_functions.items():
            info = route_meta_infos.get(func.__name__ + str(func.__hash__()), None)
            if info:
                self.manager.ep_meta.setdefault(ep, info)

    def handle_error(self, app):
        @app.errorhandler(Exception)
        def handler(e):
            if isinstance(e, APIException):
                return e
            if isinstance(e, HTTPException):
                code = e.code
                msg = e.description
                error_code = 20000
                return APIException(msg, code, error_code)
            else:
                if not app.config['DEBUG']:
                    import traceback
                    app.logger.error(traceback.format_exc())
                    return UnknownException()
                else:
                    raise e

    def _enable_json_encoder(self, app):
        app.json_encoder = JSONEncoder

    def _enable_create_all(self, app):
        with app.app_context():
            db.create_all()


class Manager(object):
    """ manager for lin """

    # 路由函数的meta信息的容器
    ep_meta = {}

    def __init__(self, plugin_path, group_model=None, user_model=None, auth_model=None):
        if not group_model:
            self.group_model = Group
        else:
            self.group_model = group_model

        if not user_model:
            self.user_model = User
        else:
            self.user_model = user_model

        if not auth_model:
            self.auth_model = Auth
        else:
            self.auth_model = auth_model

        from .loader import Loader
        self.loader: Loader = Loader(plugin_path)

    def find_user(self, **kwargs):
        return self.user_model.query.filter_by(**kwargs).first()

    def verify_user(self, username, password):
        return self.user_model.verify(username, password)

    def find_group(self, **kwargs):
        return self.group_model.query.filter_by(**kwargs).first()

    def verity_user_in_group(self, group_id, auth, module):
        return self.auth_model.query.filter_by(group_id=group_id, auth=auth, module=module).first()

    @property
    def plugins(self):
        return self.loader.plugins

    def get_plugin(self, name):
        return self.loader.plugins.get(name)

    def get_model(self, name):
        # attention!!! if models have the same name,will return the first one
        # 注意！！！ 如果容器内有相同的model，则默认返回第一个
        for plugin in self.plugins.values():
            return plugin.models.get(name)

    def get_service(self, name):
        # attention!!! if services have the same name,will return the first one
        # 注意！！！ 如果容器内有相同的service，则默认返回第一个
        for plugin in self.plugins.values():
            return plugin.services.get(name)


# a proxy for manager instance
# attention, only used when context in  stack

# 获得manager实例
# 注意，仅仅在flask的上下文栈中才可获得
manager: Manager = LocalProxy(lambda: get_manager())


def get_manager():
    _manager = current_app.extensions['manager']
    if _manager:
        return _manager
    else:
        app = current_app._get_current_object()
        with app.app_context():
            return app.extensions['manager']


class User(UserInterface, db.Model):

    @classmethod
    def verify(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user is None or user.delete_time is not None:
            raise NotFound(msg='用户不存在')
        if not user.check_password(password):
            raise ParameterException(msg='密码错误，请输入正确密码')
        if not user.is_active:
            raise AuthFailed(msg='您目前处于未激活状态，请联系超级管理员')
        return user

    def reset_password(self, new_password):
        #: attention,remember to commit
        #: 注意，修改密码后记得提交至数据库
        self.password = new_password

    def change_password(self, old_password, new_password):
        #: attention,remember to commit
        #: 注意，修改密码后记得提交至数据库
        if self.check_password(old_password):
            self.password = new_password
            return True
        return False


class Group(GroupInterface):
    pass


class Auth(AuthInterface):
    pass


# log model
class Log(LogInterface):

    @staticmethod
    def create_log(**kwargs):
        log = Log()
        for key in kwargs.keys():
            if hasattr(log, key):
                setattr(log, key, kwargs[key])
        db.session.add(log)
        if kwargs.get('commit') is True:
            db.session.commit()
        return log


# event model
class Event(EventInterface):
    pass


# file model
class File(FileInterface):

    @staticmethod
    def create_file(**kwargs):
        file = File()
        for key in kwargs.keys():
            if hasattr(file, key):
                setattr(file, key, kwargs[key])
        db.session.add(file)
        if kwargs.get('commit') is True:
            db.session.commit()
        return file


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        return JSONEncoder.default(self, o)
