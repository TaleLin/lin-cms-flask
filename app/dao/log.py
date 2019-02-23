"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import request
from lin import db
from lin.core import Log
from lin.exception import NotFound, ParameterException
from lin.util import paginate
from sqlalchemy import text


class LogDAO(Log):

    def get_by_paginate(self, form):
        start, count = paginate()
        logs = self.query.filter()
        if form.name.data:
            logs = logs.filter(Log.user_name == form.name.data)
        if form.start.data and form.end.data:
            logs = logs.filter(Log.time.between(form.start.data, form.end.data))
        total_nums = logs.count()
        logs = logs.order_by(text('time desc')).offset(start).limit(count).all()
        if not logs:
            raise NotFound(msg='没有找到相关日志')
        return logs, total_nums

    def search_by_keyword(self, form):
        keyword = request.args.get('keyword', default=None, type=str)
        if keyword is None or '':
            raise ParameterException(msg='搜索关键字不可为空')
        start, count = paginate()
        logs = self.query.filter(Log.message.like(f'%{keyword}%'))
        if form.name.data:
            logs = logs.filter(Log.user_name == form.name.data)
        if form.start.data and form.end.data:
            logs = logs.filter(Log._time.between(form.start.data, form.end.data))
        total_nums = logs.count()
        logs = logs.order_by(text('time desc')).offset(start).limit(count).all()
        if not logs:
            raise NotFound(msg='没有找到相关日志')
        return logs, total_nums

    def get_users_by_paginate(self):
        start, count = paginate()
        user_names = db.session.query(Log.user_name).filter_by(
            soft=False).group_by(text('user_name')).having(
            text('count(user_name) > 0')).offset(start).limit(count).all()
        res = [user_name[0] for user_name in user_names]
        return res
