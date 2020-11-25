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
from cli.test.util import get_token
from app.app import create_app

app = create_app()


def test_authority():
    with app.test_client() as c:
        rv = c.get('/cms/admin/authority', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        assert rv.status_code == 200


def test_delete_user():
    with app.test_client() as c:
        rv = c.delete('/cms/admin/6', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        assert rv.status_code == 201


def test_get_admin_users():
    with app.test_client() as c:
        rv = c.get('/cms/admin/users', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        json_data = rv.get_json()
        assert rv.status_code == 200
