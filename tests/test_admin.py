"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from . import get_token
from app.app import create_app

app = create_app()


def test_authority():
    with app.test_client() as c:
        rv = c.get(
            "/cms/admin/permission", headers={"Authorization": "Bearer " + get_token()}
        )
        assert rv.status_code == 200


def test_get_admin_users():
    with app.test_client() as c:
        rv = c.get(
            "/cms/admin/users", headers={"Authorization": "Bearer " + get_token()}
        )
        assert rv.status_code == 200
