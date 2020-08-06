"""
    enums of Lin
    ~~~~~~~~~
    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from enum import Enum


# status for user is admin
# 是否为超级管理员的枚举
class UserAdmin(Enum):
    COMMON = 1
    ADMIN = 2


# : status for user is active
# : 当前用户是否为激活状态的枚举
class UserActive(Enum):
    ACTIVE = 1
    NOT_ACTIVE = 2
