"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from app.app import create_app
from tests.utils import write_token, get_token

app = create_app()


def test_login():
    with app.test_client() as c:
        rv = c.post('/cms/user/login', json={
            'nickname': 'super', 'password': '123456'
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
        json_data = rv.get_json()
        print(json_data)
        assert rv.status_code == 201
