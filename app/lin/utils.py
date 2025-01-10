"""
    utils of Lin
    ~~~~~~~~~

    util functions make Lin more easy.

    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import errno
import importlib.util
import os
import random
import re
import time
import types
from collections import namedtuple
from importlib import import_module


def get_timestamp(fmt="%Y-%m-%d %H:%M:%S"):
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
        with open(path, mode="rb") as config_file:
            exec(compile(config_file.read(), path, "exec"), d.__dict__)
    except IOError as e:
        if silent and e.errno in (errno.ENOENT, errno.EISDIR, errno.ENOTDIR):
            return False
        e.strerror = "Unable to load configuration file (%s)" % e.strerror
        raise
    return d.__dict__


def load_object(path):
    """
    获得一个模块中的某个属性
    :param path: module path
    :return: the obj of module which you want get.
    """
    try:
        dot = path.rindex(".")
    except ValueError:
        raise ValueError("Error loading object '%s': not a full path" % path)

    module, name = path[:dot], path[dot + 1 :]
    mod = import_module(module)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError(
            "Module '%s' doesn't define any object named '%s'" % (module, name)
        )

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


def camel2line(camel: str):
    p = re.compile(r"([a-z]|\d)([A-Z])")
    line = re.sub(p, r"\1_\2", camel).lower()
    return line


def get_random_str(length):
    seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    sa = []
    for i in range(length):
        sa.append(random.choice(seed))
    salt = "".join(sa)
    return salt


# 路由函数的权限和模块信息(meta信息)
Meta = namedtuple("meta", ["name", "module", "mount"])

#       -> endpoint -> func
# permission                      -> module
#       -> endpoint -> func

# 记录路由函数的权限和模块信息
permission_meta_infos = {}


def permission_meta(name, module="common", mount=True):
    """
    记录路由函数的信息
    记录路由函数访问的推送信息模板
    注：只有使用了 permission_meta 装饰器的函数才会被记录到权限管理的map中
    :param name: 权限名称
    :param module: 所属模块
    :param mount: 是否挂在到权限中（一些视图函数需要说明，或暂时决定不挂在到权限中，则设置为False）
    :return:
    """

    def wrapper(func):
        func_name = func.__name__ + str(func.__hash__())
        existed = (
            permission_meta_infos.get(func_name, None)
            and permission_meta_infos.get(func_name).module == module
        )
        if existed:
            raise Exception("func_name cant't be repeat in a same module")
        else:
            permission_meta_infos.setdefault(func_name, Meta(name, module, mount))

        return func

    return wrapper
