from flask import Response, jsonify


class LinResponse(Response):
    # default_mimetype = 'application/json'   # 设置默认 response 类型，默认是 text/html

    @classmethod
    def force_type(cls, rv, environ=None):
        """
        只有当视图函数返回 WSGI callable 或者其它可调用对象时，才会调用 force_type
        具体参见 flask/app.py 中 make_response 源码部分
        :param rv: response value, a response object or wsgi application.
        :param environ: a WSGI environment object.
        :return: a response object.
        """
        if isinstance(rv, (dict, list, tuple, set)):
            rv = jsonify(rv)
        return super(LinResponse, cls).force_type(rv, environ)
