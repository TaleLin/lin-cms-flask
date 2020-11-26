"""
    A CMS of flask named Lin 😂.
     ~~~~~~~~~

    This project implements a common cms of flask

    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from .core import Lin, permission_meta, manager
from .db import db
from .jwt import login_required, group_required, admin_required
