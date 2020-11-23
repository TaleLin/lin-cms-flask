"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from app.app import create_app
from app.lin.core import manager
from app.lin.db import db


def main():
    app = create_app()
    with app.app_context():
        with db.auto_commit():
            # 创建一个超级管理员
            user = manager.user_model()
            user.username = 'root'
            user.password = '123456'
            user.email = '123456789@qq.com'
            # admin 2 的时候为超级管理员，普通用户为 1
            user.admin = 2
            db.session.add(user)
            # 添加 默认用户组
            root_group = manager.group_model()
            root_group.name = "root"
            root_group.info = "超级用户组"
            root_group.level = 1
            db.session.add(root_group)
            guest_group = manager.group_model()
            guest_group.name = "guest"
            guest_group.info = "游客组"
            guest_group.level = 2
            db.session.add(guest_group)


if __name__ == '__main__':
    try:
        main()
        print("数据库初始化成功")
    except Exception as e:
        raise e
