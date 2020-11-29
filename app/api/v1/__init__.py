"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import Blueprint

from app.api.v1 import book


def create_v1():
    bp_v1 = Blueprint("v1", __name__)
    book.book_api.register(bp_v1)
    return bp_v1
