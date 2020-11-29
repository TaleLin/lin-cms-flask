"""
    register api to admin blueprint
    ~~~~~~~~~
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import Blueprint


def create_cms():
    cms = Blueprint("cms", __name__)
    from .admin import admin_api
    from .file import file_api
    from .log import log_api
    from .user import user_api

    admin_api.register(cms)
    user_api.register(cms)
    log_api.register(cms)
    file_api.register(cms)
    return cms
