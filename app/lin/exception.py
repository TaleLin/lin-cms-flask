"""
    exceptions of Lin
    ~~~~~~~~~
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from app.lin.util import MultipleMeta
from flask import json, request
from werkzeug.exceptions import HTTPException
from werkzeug._compat import text_type


class APIException(HTTPException, metaclass=MultipleMeta):
    code = 500
    message = '抱歉，服务器未知错误'
    error_code = 9999
    headers = {'Content-Type': 'application/json'}

    def __init__(self):
        super(APIException, self).__init__(None, None)

    def __init__(self, error_code: int):
        self.error_code = error_code
        super(APIException, self).__init__(None, None)

    def __init__(self, message: str):
        self.message = message
        super(APIException, self).__init__(message, None)

    def __init__(self, error_code: int, message: str):
        self.error_code = error_code
        self.message = message
        super(APIException, self).__init__(message, None)

    def __init__(self, exception_dict: dict):
        code = exception_dict.get('code')
        error_code = exception_dict.get('error_code')
        message = exception_dict.get('message')
        headers = exception_dict.get('headers')
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if message:
            self.message = message
        if headers is not None:
            headers_merged = headers.copy()
            headers_merged.update(self.headers)
            self.headers = headers_merged

        super(APIException, self).__init__(message, None)

    def set_code(self, code: int):
        self.code = code
        return self

    def add_headers(self, headers: dict):
        headers_merged = headers.copy()
        headers_merged.update(self.headers)
        self.headers = headers_merged
        return self

    def get_body(self, environ=None):
        body = dict(
            message=self.message,
            code=self.error_code,
            request=request.method + '  ' + self.get_url_no_param()
        )
        text = json.dumps(body)
        return text_type(text)

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split('?')
        return main_path[0]

    def get_headers(self, environ=None):
        return [(k, v)for k, v in self.headers.items()]


class Success(APIException):
    code = 201
    message = 'OK'
    error_code = 0


class Created(APIException):
    code = 201
    message = 'Created'
    error_code = 1


class Updated(APIException):
    code = 201
    message = 'Updated'
    error_code = 2


class Deleted(APIException):
    code = 201
    message = 'Deleted'
    error_code = 3


class Fail(APIException):
    code = 400
    message = 'Failed'
    error_code = 10200


class UnAuthorization(APIException):
    code = 401
    message = 'Authorization Failed'
    error_code = 10000


class UnAuthentication(APIException):
    code = 401
    message = 'Authentication Failed'
    error_code = 10010


class NotFound(APIException):
    code = 404
    message = 'Not Found'
    error_code = 10021


class ParameterError(APIException):
    code = 400
    message = 'Parameters Error'
    error_code = 10030


class TokenInvalid(APIException):
    code = 401
    message = 'Token Invalid'
    error_code = 10040


class TokenExpired(APIException):
    code = 422
    message = 'Token Expired'
    error_code = 10052


class InternalServerError(APIException):
    code = 500
    message = 'Internal Server Error'
    error_code = 9999


class Duplicated(APIException):
    code = 400
    message = 'Duplicated'
    error_code = 10060


class Forbidden(APIException):
    code = 401
    message = 'Forbidden'
    error_code = 10070


class RefreshFailed(APIException):
    code = 401
    message = 'Get Refresh Token Failed'
    error_code = 10100


class FileTooLarge(APIException):
    code = 413
    message = 'File Too Large'
    error_code = 10110


class FileTooMany(APIException):
    code = 413
    message = 'File Too Many'
    error_code = 10120


class FileExtensionError(APIException):
    code = 401
    message = 'FIle Extension Not Allowed'
    error_code = 10130


class MethodNotAllowed(APIException):
    code = 401
    message = 'Method Not Allowed'
    error_code = 10080


class RequestLimit(APIException):
    code = 401
    message = 'Too Many Requests'
    error_code = 10140
