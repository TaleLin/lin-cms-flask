"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from app.lin.exception import APIException


class BookNotFound(APIException):
    code = 404  # http状态码
    message = '没有找到相关图书'  # 异常信息
    error_code = 80010  # 约定的异常码


class RefreshException(APIException):
    code = 401
    message = "refresh token 获取失败"
    error_code = 10042
