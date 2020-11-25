"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from .util import write_token, get_token
if __name__ == "__main__":
    import sys
    sys.path.append("../../")
from app.app import create_app


app = create_app()


def test_login():
    with app.test_client() as c:
        rv = c.post('/cms/user/login', json={
            'nickname': 'tester', 'password': '123456'
        })
        json_data = rv.get_json()
        print(json_data)
        write_token(json_data)
        assert json_data['access_token'] is not None
        assert rv.status_code == 200


def test_change_password():
    with app.test_client() as c:
        rv = c.put('/cms/user/', headers={
            'Authorization': 'Bearer ' + get_token()
        }, json={
            'email': '1312342604@qq.com'
        })
        assert rv.status_code == 201
