"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from lin.core import User
from lin.db import db

from app.app import create_app


def main():
    app = create_app()
    with app.app_context():
        with db.auto_commit():
            # 创建一个超级管理员
            user = User()
            user.nickname = 'super'
            user.password = '123456'
            user.email = '1234995678@qq.com'
            # admin 2 的时候为超级管理员，普通用户为 1
            user.admin = 2
            db.session.add(user)


if __name__ == '__main__':
    try:
        main()
        print("新增超级管理员成功")
    except Exception as e:
        raise e
