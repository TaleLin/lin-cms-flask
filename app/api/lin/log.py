"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

import math

from app.common.utils import get_page_from_query, paginate
from app.extension.log.log import Log
from app.lin import permission_meta
from app.lin.db import db
from app.lin.exception import NotFound, ParameterError
from app.lin.jwt import group_required
from app.lin.redprint import Redprint
from app.validator.form import LogFindForm
from flask import request
from sqlalchemy import text

log_api = Redprint("log")


# 日志浏览（人员，时间），分页展示
@log_api.route("", methods=["GET"])
@permission_meta(auth="查询所有日志", module="日志")
@group_required
def get_logs():
    form = LogFindForm().validate_for_api()
    start, count = paginate()
    logs = db.session.query(Log).filter()
    if form.name.data:
        logs = logs.filter(Log.username == form.name.data)
    if form.start.data and form.end.data:
        logs = logs.filter(Log.create_time.between(form.start.data, form.end.data))
    total = logs.count()
    logs = logs.order_by(text("create_time desc")).offset(start).limit(count).all()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    if not logs:
        logs = []
    return {
        "page": page,
        "count": count,
        "total": total,
        "items": logs,
        "total_page": total_page,
    }


# 日志搜素（人员，时间）（内容）， 分页展示
@log_api.route("/search", methods=["GET"])
@permission_meta(auth="搜索日志", module="日志")
@group_required
def get_user_logs():
    form = LogFindForm().validate_for_api()
    keyword = request.args.get("keyword", default=None, type=str)
    if keyword is None or str():
        raise ParameterError("搜索关键字不可为空")
    start, count = paginate()
    logs = Log.query.filter(Log.message.like(f"%{keyword}%"))
    if form.name.data:
        logs = logs.filter(Log.username == form.name.data)
    if form.start.data and form.end.data:
        logs = logs.filter(Log.create_time.between(form.start.data, form.end.data))
    total = logs.count()
    logs = logs.order_by(text("create_time desc")).offset(start).limit(count).all()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    if not logs:
        logs = []
    return {
        "page": page,
        "count": count,
        "total": total,
        "items": logs,
        "total_page": total_page,
    }


@log_api.route("/users", methods=["GET"])
@permission_meta(auth="查询日志记录的用户", module="日志")
@group_required
def get_users():
    start, count = paginate()
    usernames = (
        db.session.query(Log.username)
        .filter_by(soft=False)
        .group_by(text("username"))
        .having(text("count(username) > 0"))
        .offset(start)
        .limit(count)
        .all()
    )
    users = [username[0] for username in usernames]
    return users
