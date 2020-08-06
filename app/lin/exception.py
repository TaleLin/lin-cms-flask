"""
    exceptions of Lin
    ~~~~~~~~~
    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask import json, request
from werkzeug.exceptions import HTTPException
from werkzeug._compat import text_type


class APIException(HTTPException):
    code = 500
    msg = '抱歉，服务器未知错误'
    error_code = 999

    def __init__(self, msg=None, code=None, error_code=None,
                 headers=None):
        if code:
            self.code = code
        if error_code:
            self.error_code = error_code
        if msg:
            self.msg = msg
        if headers is not None:
            headers_merged = headers.copy()
            headers_merged.update(self.headers)
            self.headers = headers_merged

        super(APIException, self).__init__(msg, None)

    def get_body(self, environ=None):
        body = dict(
            message=self.msg,
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
        return [('Content-Type', 'application/json')]


class Success(APIException):
    code = 201
    msg = 'OK'
    error_code = 0


class Created(APIException):
    code = 201
    msg = 'Created'
    error_code = 1


class Updated(APIException):
    code = 201
    msg = 'Updated'
    error_code = 2


class Deleted(APIException):
    code = 201
    msg = 'Deleted'
    error_code = 3


class Fail(APIException):
    code = 400
    msg = 'Failed'
    error_code = 10200


class UnAuthorization(APIException):
    code = 401
    msg = 'Authorization Failed'
    error_code = 10000


class UnAuthentication(APIException):
    code = 401
    msg = 'Authentication Failed'
    error_code = 10010


class NotFound(APIException):
    code = 404
    msg = 'Not Found'
    error_code = 10021


class ParameterError(APIException):
    code = 400
    msg = 'Parameters Error'
    error_code = 10030


class TokenInvalid(APIException):
    code = 401
    msg = 'Token Invalid'
    error_code = 10040


class TokenExpired(APIException):
    code = 422
    msg = 'Token Expired'
    error_code = 10050


class InternalServerError(APIException):
    code = 500
    msg = 'Internal Server Error'
    error_code = 9999


class Duplicated(APIException):
    code = 400
    msg = 'Duplicated'
    error_code = 10060


class Forbidden(APIException):
    code = 401
    msg = 'Forbidden'
    error_code = 10070


class RefreshFailed(APIException):
    code = 401
    msg = 'Get Refresh Token Failed'
    error_code = 10100


class FileTooLarge(APIException):
    code = 413
    msg = 'File Too Large'
    error_code = 10110


class FileTooMany(APIException):
    code = 413
    msg = 'File Too Many'
    error_code = 10120


class FileExtensionError(APIException):
    code = 401
    msg = 'FIle Extension Not Allowed'
    error_code = 10130


class MethodNotAllowed(APIException):
    code = 401
    msg = 'Method Not Allowed'
    error_code = 10080


class RequestLimit(APIException):
    code = 401
    msg = 'Too Many Requests'
    error_code = 10140
