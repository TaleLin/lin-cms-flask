"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

import math

from flask import g, request
from lin import DocResponse, permission_meta
from lin.db import db
from lin.exception import DocParameterError, NotFound, ParameterError
from lin.jwt import group_required
from lin.logger import Log
from lin.redprint import Redprint
from sqlalchemy import text
from sqlalchemy.orm import query

from app.api import apidoc
from app.util.page import get_page_from_query, paginate
from app.validator.form import LogFindForm
from app.validator.schema import AccessTokenSchema, LogListSchema, LogQuerySearchSchema

log_api = Redprint("log")


# 日志浏览（人员，时间, 关键字），分页展示
@log_api.route("")
@log_api.route("/search")
@permission_meta(auth="查询日志", module="日志")
@group_required
@apidoc.validate(
    headers=AccessTokenSchema,
    query=LogQuerySearchSchema,
    resp=DocResponse(DocParameterError, http_200=LogListSchema),
    before=LogQuerySearchSchema.offset_handler,
    tags=["日志"],
)
def get_logs():
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
def get_users():
    usernames_dict = db.query(
        """
    SELECT l.username
    FROM lin_log l
    WHERE l.delete_time IS NULL
    GROUP BY l.username
    HAVING COUNT(l.username) > 0
    """
    ).as_dict()
    return {"items": [ud.get("username") for ud in usernames_dict]}
