from lin.exception import Duplicated, Failed, NotFound


class BookNotFound(NotFound):
    message = "书籍不存在"
    _config = False


class BookDuplicated(Duplicated):
    code = 419
    message = "图书已存在"
    _config = False


class RefreshFailed(Failed):
    message = "令牌刷新失败"
    message_code = 10052
    _config = False
