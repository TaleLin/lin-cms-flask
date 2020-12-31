import json
import os

import pytest

from app import create_app
from app.model.lin import (
    Group,
    GroupPermission,
    Permission,
    User,
    UserGroup,
    UserIdentity,
)

from .config import password, username

app = create_app(
    group_model=Group,
    user_model=User,
    group_permission_model=GroupPermission,
    permission_model=Permission,
    identity_model=UserIdentity,
    user_group_model=UserGroup,
)


@pytest.fixture()
def fixtureFunc():
    with app.test_client() as c:
        rv = c.post(
            "/cms/user/login",
            headers={"Content-Type": "application/json"},
            json={"username": username, "password": password},
        )
        json_data = rv.get_json()
        assert json_data.get("access_token") != None
        assert rv.status_code == 200
        write_token(json_data)


def get_file_path():
    pytest_cache_dir_path = os.getcwd() + os.path.sep + ".pytest_cache"
    if not os.path.exists(pytest_cache_dir_path):
        os.makedirs(pytest_cache_dir_path)
    json_file_path = pytest_cache_dir_path + os.path.sep + "test.json"
    return json_file_path


def write_token(data):
    obj = json.dumps(data)
    with open(get_file_path(), "w") as f:
        f.write(obj)


def get_token(key="access_token"):
    with open(get_file_path(), "r") as f:
        obj = json.loads(f.read())
        return obj[key]
