import math

from flask import g
from lin import permission_meta
from lin.apidoc import DocResponse, api
from lin.db import db
from lin.jwt import group_required
from lin.logger import Log
from lin.redprint import Redprint
from sqlalchemy import text

from app.validator.schema import (
    AuthorizationSchema,
    LogPageSchema,
    LogQuerySearchSchema,
    UsernameListSchema,
)

log_api = Redprint("log")


@log_api.route("")
@log_api.route("/search")
@permission_meta(name="查询日志", module="日志")
# @group_required
@api.validate(
    headers=AuthorizationSchema,
    query=LogQuerySearchSchema,
    resp=DocResponse(r=LogPageSchema),
    before=LogQuerySearchSchema.offset_handler,
    tags=["日志"],
)
def get_logs():
    """
    日志浏览查询（人员，时间, 关键字），分页展示
    """
    if g.keyword:
        logs = Log.query.filter(Log.message.like(f"%{g.keyword}%"))
    else:
        logs = Log.query.filter()
    if g.name:
        logs = logs.filter(Log.username == g.name)
    if g.start and g.end:
        logs = logs.filter(Log.create_time.between(g.start, g.end))

    total = logs.count()
    items = (
        logs.order_by(text("create_time desc")).offset(g.offset).limit(g.count).all()
    )
    total_page = math.ceil(total / g.count)

    return LogPageSchema(
        page=g.page, count=g.count, total=total, items=items, total_page=total_page
    )


@log_api.route("/users")
@permission_meta(name="查询日志记录的用户", module="日志")
@group_required
@api.validate(
    headers=AuthorizationSchema,
    resp=DocResponse(r=UsernameListSchema),
    tags=["日志"],
)
def get_users_for_log():
    """
    获取所有记录行为日志的用户名
    """
    usernames = (
        db.session.query(Log.username)
        .filter_by(soft=False)
        .group_by(text("username"))
        .having(text("count(username) > 0"))
        .all()
    )
    return UsernameListSchema(items=[u.username for u in usernames])
