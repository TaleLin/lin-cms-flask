"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from app.app import create_app
from tests.utils import get_token

app = create_app()


def test_authority():
    with app.test_client() as c:
        rv = c.get('/cms/admin/authority', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        json_data = rv.get_json()
        print(json_data)
        assert rv.status_code == 200


def test_delete_user():
    with app.test_client() as c:
        rv = c.delete('/cms/admin/6', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        json_data = rv.get_json()
        print(json_data)
        assert rv.status_code == 201


def test_get_admin_users():
    with app.test_client() as c:
        rv = c.get('/cms/admin/users', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        json_data = rv.get_json()
        print(len(json_data['collection']))
        assert rv.status_code == 200
