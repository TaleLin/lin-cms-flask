from flask import Flask, jsonify
from app.libs.lin_response import LinResponse


class LinFlask(Flask):
    response_class = LinResponse

    def make_response(self, rv, types: iter = (list, set)):
        """
        基本用途为将视图函数返回的值转换为flask内置支持的类型
        string, dict, tuple, Response instance, or WSGI callable
        例如：默认将 list 和 set 类型直接转换为json类型返回，
        这样就不需要在每个视图函数返回的时候都调用 jsonify
        代码更加简洁

        如果需要对视图函数返回的值进行统一的处理和封装，也可以在此函数下进行

        :param rv: response value
        :param types: types to change
        :return:
        """
        if isinstance(rv, types):
            rv = jsonify(rv)
        return super(LinFlask, self).make_response(rv)
