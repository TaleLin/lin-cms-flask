"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

import math

from flask import g, request
from lin import permission_meta
from lin.db import db
from lin.exception import NotFound, ParameterError
from lin.jwt import group_required
from lin.logger import Log
from lin.redprint import Redprint
from sqlalchemy import text
from sqlalchemy.orm import query

from app.api import apidoc
from app.util.page import get_page_from_query, paginate
from app.validator.form import LogFindForm
from app.validator.schema import AccessTokenSchema, QuerySearchSchema

log_api = Redprint("log")


# 日志浏览（人员，时间），分页展示
@log_api.route("", methods=["GET"])
@permission_meta(auth="查询所有日志", module="日志")
@group_required
@apidoc.validate(
    headers=AccessTokenSchema,
    query=QuerySearchSchema,
    before=QuerySearchSchema.before_handler,
    after=QuerySearchSchema.after_handler,
    tags=["日志"],
)
def get_logs():
    query_search_schema = request.context.query
    count = query_search_schema.count
    page = query_search_schema.page
    name = query_search_schema.name
    start = query_search_schema.start
    end = query_search_schema.end
    logs = db.session.query(Log).filter()
    if name:
        logs = logs.filter(Log.username == name)
    if start and end:
        logs = logs.filter(Log.create_time.between(start, end))
    total = logs.count()
    logs = logs.order_by(text("create_time desc")).offset(g.offset).limit(count).all()
    total_page = math.ceil(total / count)
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
