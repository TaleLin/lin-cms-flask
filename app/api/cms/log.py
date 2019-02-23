"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import jsonify
from lin.core import route_meta
from lin.jwt import group_required
from lin.redprint import Redprint

from app.dao.log import LogDAO
from app.validators.forms import LogFindForm

log_api = Redprint('log')


# 日志浏览（人员，时间），分页展示
@log_api.route('/', methods=['GET'], strict_slashes=False)
@route_meta(auth='查询所有日志', module='日志')
@group_required
def get_logs():
    form = LogFindForm().validate_for_api()
    logs, total_nums = LogDAO().get_by_paginate(form)
    return jsonify({
        "total_nums": total_nums,
        "collection": logs
    })


# 日志搜素（人员，时间）（内容）， 分页展示
@log_api.route('/search', methods=['GET'])
@route_meta(auth='搜索日志', module='日志')
@group_required
def get_user_logs():
    form = LogFindForm().validate_for_api()
    logs, total_nums = LogDAO().search_by_keyword(form)
    return jsonify({
        "total_nums": total_nums,
        "collection": logs
    })


@log_api.route('/users', methods=['GET'])
@route_meta(auth='查询日志记录的用户', module='日志')
@group_required
def get_users():
    users = LogDAO().get_users_by_paginate()
    return jsonify(users)
