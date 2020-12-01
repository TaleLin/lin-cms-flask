"""
common exception 
"""


from lin.exception import NotFound, ParameterError


class BookNotFound(NotFound):
    message = "书籍不存在"


class BookParameterError(ParameterError):
    message = "书籍参数错误"
