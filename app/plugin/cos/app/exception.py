from lin import NotFound


class ImageNotFound(NotFound):
    message = "图片不存在"
    _config = False
