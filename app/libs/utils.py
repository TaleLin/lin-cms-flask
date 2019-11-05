"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

import re
import time

from flask import current_app, jsonify, request
from lin.exception import ParameterException


def get_timestamp(fmt='%Y-%m-%d %H:%M:%S'):
    return time.strftime(fmt, time.localtime(time.time()))


def get_count_from_query():
    count_default = current_app.config.get('COUNT_DEFAULT')
    count = int(request.args.get('count', count_default if count_default else 1))
    return count


def get_page_from_query():
    page_default = current_app.config.get('PAGE_DEFAULT')
    page = int(request.args.get('page', page_default if page_default else 0))
    return page


def paginate():
    _count = get_count_from_query()
    count = 15 if _count >= 15 else _count
    start = get_page_from_query() * count
    if start < 0 or count < 0:
        raise ParameterException()
    return start, count


def camel2line(camel: str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    line = re.sub(p, r'\1_\2', camel).lower()
    return line


def json_res(**kwargs):
    '''
    将所有传入的关键字参数转变为dict后序列化为json格式的response
    count, items, page, total, total_page ...
    '''
    return jsonify(kwargs)
