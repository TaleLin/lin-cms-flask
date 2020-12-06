"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from . import get_token, app


def test_a_authority():
    with app.test_client() as c:
        rv = c.get(
            "/cms/admin/permission", headers={"Authorization": "Bearer " + get_token()}
        )
        assert rv.status_code == 200


def test_b_get_admin_users():
    with app.test_client() as c:
        rv = c.get(
            "/cms/admin/users", headers={"Authorization": "Bearer " + get_token()}
        )
        assert rv.status_code == 200
