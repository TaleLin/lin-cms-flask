from lin import Duplicated, NotFound


class BookNotFound(NotFound):
    message = "书籍不存在"
    _config = False


class BookDuplicated(Duplicated):
    code = 419
    message = "图书已存在"
    _config = False
