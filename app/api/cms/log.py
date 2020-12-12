import math

from flask import g
from lin import DocResponse, lindoc, permission_meta
from lin.db import db
from lin.jwt import group_required
from lin.logger import Log
from lin.redprint import Redprint
from sqlalchemy import text

from app.validator.schema import (
    AccessTokenSchema,
    LogListSchema,
    LogQuerySearchSchema,
    NameListSchema,
)

log_api = Redprint("log")


@log_api.route("")
@log_api.route("/search")
@permission_meta(auth="查询日志", module="日志")
@group_required
@lindoc.validate(
    headers=AccessTokenSchema,
    query=LogQuerySearchSchema,
    resp=DocResponse(http_200=LogListSchema),
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

    return LogListSchema(
        page=g.page, count=g.count, total=total, items=items, total_page=total_page
    )


@log_api.route("/users", methods=["GET"])
@permission_meta(auth="查询日志记录的用户", module="日志")
@group_required
@lindoc.validate(
    headers=AccessTokenSchema,
    resp=DocResponse(http_200=NameListSchema),
    tags=["日志"],
)
def get_users_for_log():
    """
    获取所有记录行为日志的用户名
    """
    usernames_dict = db.query(
        """
    SELECT l.username
    FROM lin_log l
    WHERE l.delete_time IS NULL
    GROUP BY l.username
    HAVING COUNT(l.username) > 0
    """
    ).as_dict()
    return NameListSchema(items=[ud.get("username") for ud in usernames_dict])
