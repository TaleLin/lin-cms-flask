"""
common exception 
"""


from lin.exception import NotFound, ParameterError, Failed


class BookNotFound(NotFound):
    message = "书籍不存在"


class BookParameterError(ParameterError):
    message = "书籍参数错误"


class RefreshFailed(Failed):
    message = "令牌刷新失败"
    message_code = 10052


