"""
    utils of Lin
    ~~~~~~~~~

    util functions make Lin more easy.

    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import errno
import importlib.util
import inspect
import os
import random
import re
import time
import types
from importlib import import_module

from flask import current_app, request


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
        raise NameError(
            "Module '%s' doesn't define any object named '%s'" % (module, name))

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
    from .exception import ParameterError
    count = int(request.args.get('count', current_app.config.get('COUNT_DEFAULT') if current_app.config.get(
        'COUNT_DEFAULT') else 5))
    start = int(request.args.get('page', current_app.config.get('PAGE_DEFAULT') if current_app.config.get(
        'PAGE_DEFAULT') else 0))
    count = 15 if count >= 15 else count
    start = start * count
    if start < 0 or count < 0:
        raise ParameterError()
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


class MultiMethod:
    '''
    Represents a single multimethod.
    '''

    def __init__(self, name):
        self._methods = {}
        self.__name__ = name

    def register(self, meth):
        '''
        Register a new method as a multimethod
        '''
        sig = inspect.signature(meth)

        # Build a type signature from the method's annotations
        types = []
        for name, parm in sig.parameters.items():
            if name == 'self':
                continue
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(
                    'Argument {} must be annotated with a type'.format(name)
                )
            if not isinstance(parm.annotation, type):
                raise TypeError(
                    'Argument {} annotation must be a type'.format(name)
                )
            if parm.default is not inspect.Parameter.empty:
                self._methods[tuple(types)] = meth
            types.append(parm.annotation)

        self._methods[tuple(types)] = meth

    def __call__(self, *args):
        '''
        Call a method based on type signature of the arguments
        '''
        types = tuple(type(arg) for arg in args[1:])
        meth = self._methods.get(types, None)
        if meth:
            return meth(*args)
        else:
            raise TypeError('No matching method for types {}'.format(types))

    def __get__(self, instance, cls):
        '''
        Descriptor method needed to make calls work in a class
        '''
        if instance is not None:
            return types.MethodType(self, instance)
        else:
            return self


class MultiDict(dict):
    '''
    Special dictionary to build multimethods in a metaclass
    '''

    def __setitem__(self, key, value):
        if key in self:
            # If key already exists, it must be a multimethod or callable
            current_value = self[key]
            if isinstance(current_value, MultiMethod):
                current_value.register(value)
            else:
                mvalue = MultiMethod(key)
                mvalue.register(current_value)
                mvalue.register(value)
                super().__setitem__(key, mvalue)
        else:
            super().__setitem__(key, value)


class MultipleMeta(type):
    '''
    Metaclass that allows multiple dispatch of methods
    '''
    def __new__(cls, clsname, bases, clsdict):
        return type.__new__(cls, clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()
