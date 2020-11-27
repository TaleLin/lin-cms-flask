"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from datetime import timedelta
import os


def getenv():
    os.getenv("FLASK_ENV", "production").upper()


class __BaseConfig(object):
    """
    基础配置
    """

    # 分页配置
    COUNT_DEFAULT = 10
    PAGE_DEFAULT = 0

    # 屏蔽 sql alchemy 的 FSADeprecationWarning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 兼容中文
    JSON_AS_ASCII = False

    SECRET_KEY = os.getenv(
        "{env}_SECRET_KEY".format(env=getenv()),
        "https://github.com/Talelin/lin-cms-flask",
    )

    # 指定数据库
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "{env}_SQLALCHEMY_DATABASE_URI".format(env=getenv()),
        "sqlite:////" + os.getcwd() + os.path.sep + "lincms.db",
    )

    # sqlachemy 终端回显
    SQLALCHEMY_ECHO = os.getenv("{env}_SQLALCHEMY_ECHO".format(env=getenv()), False)


class DevelopmentConfig(__BaseConfig):
    """
    开发环境普通配置
    """

    # 令牌配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # 插件模块暂时没有开启，以下配置可忽略
    # plugin config写在字典里面
    PLUGIN_PATH = {
        "poem": {
            "path": "app.plugin.poem",
            "enable": True,
            "version": "0.0.1",
            "limit": 20,
        },
        "oss": {
            "path": "app.plugin.oss",
            "enable": True,
            "version": "0.0.1",
            "access_key_id": "not complete",
            "access_key_secret": "not complete",
            "endpoint": "http://oss-cn-shenzhen.aliyuncs.com",
            "bucket_name": "not complete",
            "upload_folder": "app",
            "allowed_extensions": ["jpg", "gif", "png", "bmp"],
        },
    }


class ProductionConfig(__BaseConfig):
    """
    生产环境普通配置
    """

    # 令牌配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # 插件模块暂时没有开启，以下配置可忽略
    # plugin config写在字典里面
    PLUGIN_PATH = {
        "poem": {
            "path": "app.plugin.poem",
            "enable": True,
            "version": "0.0.1",
            "limit": 20,
        },
        "oss": {
            "path": "app.plugin.oss",
            "enable": True,
            "version": "0.0.1",
            "access_key_id": "not complete",
            "access_key_secret": "not complete",
            "endpoint": "http://oss-cn-shenzhen.aliyuncs.com",
            "bucket_name": "not complete",
            "upload_folder": "app",
            "allowed_extensions": ["jpg", "gif", "png", "bmp"],
        },
    }


class TestConfig(__BaseConfig):
    """
    测试环境普通配置
    """

    # 令牌配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # 插件模块暂时没有开启，以下配置可忽略
    # plugin config写在字典里面
    PLUGIN_PATH = {
        "poem": {
            "path": "app.plugin.poem",
            "enable": True,
            "version": "0.0.1",
            "limit": 20,
        },
        "oss": {
            "path": "app.plugin.oss",
            "enable": True,
            "version": "0.0.1",
            "access_key_id": "not complete",
            "access_key_secret": "not complete",
            "endpoint": "http://oss-cn-shenzhen.aliyuncs.com",
            "bucket_name": "not complete",
            "upload_folder": "app",
            "allowed_extensions": ["jpg", "gif", "png", "bmp"],
        },
    }
