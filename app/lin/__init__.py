"""
    A CMS of flask named Lin 😂.
     ~~~~~~~~~

    This project implements a common cms of flask

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from .core import Lin, route_meta, manager
from .db import db
from .jwt import login_required, group_required, admin_required
