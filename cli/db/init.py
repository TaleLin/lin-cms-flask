"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import os
if __name__ == "__main__":
    import sys
    sys.path.append("../../")
from app.app import create_app
from app.lin.core import manager
from app.lin.db import db


def init():
    app = create_app()
    with app.app_context():
        if manager.user_model.query.all() or manager.user_group_model.query.all() or manager.group_model.query.all():
            print("表中存在数据，初始化失败")
            os._exit(-1)
        with db.auto_commit():
            # 创建一个超级管理员分组
            root_group = manager.group_model()
            root_group.name = "root"
            root_group.info = "超级用户组"
            root_group.level = 1
            db.session.add(root_group)
            # 创建一个超级管理员
            user = manager.user_model()
            user.username = 'root'
            user.password = '123456'
            user.email = '123456789@qq.com'
            user.admin = 2
            db.session.add(user)
            # root用户id为1， 超级管理员分组id为1, 将对应关系写入user_group表中
            user_group = manager.user_group_model()
            user_group.user_id = 1
            user_group.group_id = 1
            db.session.add(user_group)
            # 添加 默认用户组 guest
            guest_group = manager.group_model()
            guest_group.name = "guest"
            guest_group.info = "游客组"
            guest_group.level = 2
            db.session.add(guest_group)
    print("数据库初始化成功")


if __name__ == '__main__':
    try:
        init()
    except Exception as e:
        raise e
