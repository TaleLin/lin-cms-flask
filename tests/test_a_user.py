"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""


from . import app, get_token, write_token


def test_a_login():
    with app.test_client() as c:
        rv = c.post(
            "/cms/user/login",
            headers={"Content-Type": "application/json"},
            json={"username": "root", "password": "123456"},
        )
        json_data = rv.get_json()
        write_token(json_data)
        assert json_data.get("access_token") != None
        assert rv.status_code == 200


def test_b_change_nickname():
    with app.test_client() as c:
        rv = c.put(
            "/cms/user",
            headers={"Authorization": "Bearer " + get_token()},
            json={"nickname": "tester"},
        )
        assert rv.status_code == 201
