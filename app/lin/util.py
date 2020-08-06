"""
    utils of Lin
    ~~~~~~~~~

    util functions make Lin more easy.

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import time
import re
import errno
import random
import types
from importlib import import_module
import os
import importlib.util
from flask import request, current_app

from .exception import ParameterException


def get_timestamp(fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime(time.time()))


def get_pyfile(path, module_name, silent=False):
    """
    get all properties of a pyfile
    获得一个.py文件的所有属性
    :param path: path of pytfile
    :param module_name: name
    :param silent: show the error or not
    :return: all properties of a pyfile
    """
    d = types.ModuleType(module_name)
    d.__file__ = path
    try:
        with open(path, mode='rb') as config_file:
            exec(compile(config_file.read(), path, 'exec'), d.__dict__)
    except IOError as e:
        if silent and e.errno in (
                errno.ENOENT, errno.EISDIR, errno.ENOTDIR
        ):
            return False
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return d.__dict__


def load_object(path):
    """
    获得一个模块中的某个属性
    :param path: module path
    :return: the obj of module which you want get.
    """
    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1:]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError("Module '%s' doesn't define any object named '%s'" % (module, name))

    return obj


def import_module_abs(name, path):
    """
    绝对路径导入模块
    :param name: name of module
    :param path: absolute path of module
    :return: the module
    """
    spec = importlib.util.spec_from_file_location(name, path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)


def get_pwd():
    """
    :return: absolute current work path
    """
    return os.path.abspath(os.getcwd())


def paginate():
    count = int(request.args.get('count', current_app.config.get('COUNT_DEFAULT') if current_app.config.get(
        'COUNT_DEFAULT') else 5))
    start = int(request.args.get('page', current_app.config.get('PAGE_DEFAULT') if current_app.config.get(
        'PAGE_DEFAULT') else 0))
    count = 15 if count >= 15 else count
    start = start * count
    if start < 0 or count < 0:
        raise ParameterException()
    return start, count


def camel2line(camel: str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    line = re.sub(p, r'\1_\2', camel).lower()
    return line


def get_random_str(length):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
    salt = ''.join(sa)
    return salt
