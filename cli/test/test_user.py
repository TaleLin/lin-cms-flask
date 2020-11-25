"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

if __name__ == "__main__":
    import sys
    import os
    current_path = os.path.abspath(__file__)
    # 获取当前文件的父目录
    father_path = os.path.abspath(
        os.path.dirname(current_path) + os.path.sep + ".")

    os.chdir(father_path)
    # 切换到项目根目录
    sys.path.append("../../")
from cli.test.util import get_token, write_token
from app.app import create_app


app = create_app()


def test_login():
    with app.test_client() as c:
        rv = c.post('/cms/user/login', json={
            'username': 'root', 'password': '123456'
        })
        json_data = rv.get_json()
        print(json_data)
        write_token(json_data)
        assert json_data['access_token'] is not None
        assert rv.status_code == 200


def test_change_nickname():
    with app.test_client() as c:
        rv = c.put('/cms/user', headers={
            'Authorization': 'Bearer ' + get_token()
        }, json={
            'nickname': 'tester'
        })
        assert rv.status_code == 201

if __name__ == "__main__":
    test_login()
    test_change_nickname()
