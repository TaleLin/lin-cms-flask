from enum import Enum


# 图片保存在本地还是云端
# 建议云端
class LocalOrCloud(Enum):
    LOCAL = 1
    CLOUD = 2
