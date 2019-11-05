"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import math

from app.libs.utils import get_page_from_query, json_res
from app.validators.forms import LogFindForm
from flask import jsonify, request
from lin import db
from lin.core import Log, route_meta
from lin.exception import NotFound, ParameterException
from lin.jwt import group_required
from lin.redprint import Redprint
from lin.util import paginate
from sqlalchemy import text

log_api = Redprint('log')


# 日志浏览（人员，时间），分页展示
@log_api.route('', methods=['GET'])
@route_meta(auth='查询所有日志', module='日志')
@group_required
def get_logs():
    form = LogFindForm().validate_for_api()
    start, count = paginate()
    logs = db.session.query(Log).filter()
    if form.name.data:
        logs = logs.filter(Log.user_name == form.name.data)
    if form.start.data and form.end.data:
        logs = logs.filter(Log.time.between(form.start.data, form.end.data))
    total = logs.count()
    logs = logs.order_by(text('time desc')).offset(start).limit(count).all()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    if not logs:
        logs = []
    return json_res(page=page, count=count, total=total, items=logs, total_page=total_page)


# 日志搜素（人员，时间）（内容）， 分页展示
@log_api.route('/search', methods=['GET'])
@route_meta(auth='搜索日志', module='日志')
@group_required
def get_user_logs():
    form = LogFindForm().validate_for_api()
    keyword = request.args.get('keyword', default=None, type=str)
    if keyword is None or '':
        raise ParameterException(msg='搜索关键字不可为空')
    start, count = paginate()
    logs = Log.query.filter(Log.message.like(f'%{keyword}%'))
    if form.name.data:
        logs = logs.filter(Log.user_name == form.name.data)
    if form.start.data and form.end.data:
        logs = logs.filter(Log._time.between(form.start.data, form.end.data))
    total = logs.count()
    logs = logs.order_by(text('time desc')).offset(start).limit(count).all()
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    if not logs:
        logs = []
    return json_res(page=page, count=count, total=total, items=logs, total_page=total_page)


@log_api.route('/users', methods=['GET'])
@route_meta(auth='查询日志记录的用户', module='日志')
@group_required
def get_users():
    start, count = paginate()
    user_names = db.session.query(Log.user_name).filter_by(
        soft=False).group_by(text('user_name')).having(
        text('count(user_name) > 0')).offset(start).limit(count).all()
    users = [user_name[0] for user_name in user_names]
    return jsonify(users)
