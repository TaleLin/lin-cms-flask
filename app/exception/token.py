from lin.exception import Failed


class RefreshFailed(Failed):
    message = "令牌刷新失败"
    message_code = 10052


