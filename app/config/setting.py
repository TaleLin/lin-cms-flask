"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from datetime import timedelta
import os


class BaseConfig(object):
    """
    基础配置
    """

    # 默认文件上传配置
    FILE = {
        "STORE_DIR": "app/assets",
        "SINGLE_LIMIT": 1024 * 1024 * 2,
        "TOTAL_LIMIT": 1024 * 1024 * 20,
        "NUMS": 10,
        "INCLUDE": set(["jpg", "png", "jpeg"]),
        "EXCLUDE": set([]),
    }

    # 运行日志
    LOG = {
        "LEVEL": "DEBUG",
        "DIR": "logs",
        "SIZE_LIMIT": 1024 * 1024 * 5,
        "REQUEST_LOG": True,
        "FILE": True,
    }
    # 分页配置
    COUNT_DEFAULT = 10
    PAGE_DEFAULT = 0

    # 屏蔽 sql alchemy 的 FSADeprecationWarning
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 兼容中文
    JSON_AS_ASCII = False

    SECRET_KEY = os.getenv("SECRET_KEY", "https://github.com/Talelin/lin-cms-flask")

    # 指定数据库
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:////" + os.getcwd() + os.path.sep + "lincms.db",
    )

    # 插件模块暂时没有开启，以下配置可忽略
    # plugin config写在字典里面

    # PLUGIN_PATH = {
    #     "poem": {
    #         "path": "app.plugin.poem",
    #         "enable": True,
    #         "version": "0.0.1",
    #         "limit": 20,
    #     },
    #     "oss": {
    #         "path": "app.plugin.oss",
    #         "enable": True,
    #         "version": "0.0.1",
    #         "access_key_id": "not complete",
    #         "access_key_secret": "not complete",
    #         "endpoint": "http://oss-cn-shenzhen.aliyuncs.com",
    #         "bucket_name": "not complete",
    #         "upload_folder": "app",
    #         "allowed_extensions": ["jpg", "gif", "png", "bmp"],
    #     },
    # }


class DevelopmentConfig(BaseConfig):
    """
    开发环境普通配置
    """

    # 令牌配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class ProductionConfig(BaseConfig):
    """
    生产环境普通配置
    """

    # 令牌配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)


class TestingConfig(BaseConfig):
    """
    测试环境普通配置
    """

    # 令牌配置
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
