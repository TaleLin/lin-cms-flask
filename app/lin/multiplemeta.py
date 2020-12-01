'''
"""
    MultipleMeta of Lin
    ~~~~~~~~~

    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
'''


import inspect
import types

__all__ = ["MultipleMeta"]


class MultiMethod:
    """
    Represents a single multimethod.
    """

    def __init__(self, name):
        self._methods = {}
        self.__name__ = name

    def register(self, meth):
        """
        Register a new method as a multimethod
        """
        sig = inspect.signature(meth)

        # Build a type signature from the method's annotations
        types = []
        for name, parm in sig.parameters.items():
            if name == "self":
                continue
            if parm.annotation is inspect.Parameter.empty:
                raise TypeError(
                    "Argument {} must be annotated with a type".format(name)
                )
            if not isinstance(parm.annotation, type):
                raise TypeError("Argument {} annotation must be a type".format(name))
            if parm.default is not inspect.Parameter.empty:
                self._methods[tuple(types)] = meth
            types.append(parm.annotation)

        self._methods[tuple(types)] = meth

    def __call__(self, *args):
        """
        Call a method based on type signature of the arguments
        """
        types = tuple(type(arg) for arg in args[1:])
        meth = self._methods.get(types, None)
        if meth:
            return meth(*args)
        else:
            raise TypeError("No matching method for types {}".format(types))

    def __get__(self, instance, cls):
        """
        Descriptor method needed to make calls work in a class
        """
        if instance is not None:
            return types.MethodType(self, instance)
        else:
            return self


class MultiDict(dict):
    """
    Special dictionary to build multimethods in a metaclass
    """

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
    """
    Metaclass that allows multiple dispatch of methods
    """

    def __new__(cls, clsname, bases, clsdict):
        return type.__new__(cls, clsname, bases, dict(clsdict))

    @classmethod
    def __prepare__(cls, clsname, bases):
        return MultiDict()
