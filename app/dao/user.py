# -*- coding: utf8 -*-
from flask import request
from flask_jwt_extended import get_current_user
from lin import db
from lin.core import find_user, manager, User as LinUser
from lin.db import get_total_nums
from lin.enums import UserSuper, UserActive
from lin.exception import NotFound, ParameterException, Forbidden, RepeatException
from sqlalchemy import and_

from app.libs.utils import paginate
from app.validators.forms import RegisterForm

__author__ = 'Colorful'
__date__ = '2019/2/23 5:10 PM'


class UserDAO(LinUser):

    def get_all(self):
        start, count = paginate()
        group_id = request.args.get('group_id')
        condition = {
            'super': UserSuper.COMMON.value,
            'group_id': group_id
        } if group_id else {
            'super': UserSuper.COMMON.value
        }

        users = db.session.query(
            manager.user_model, manager.group_model.name
        ).filter_by(soft=True, **condition).join(
            manager.group_model,
            manager.user_model.group_id == manager.group_model.id
        ).offset(start).limit(count).all()

        user_and_group = []
        for user, group_name in users:
            setattr(user, 'group_name', group_name)
            user._fields.append('group_name')
            user.hide('update_time', 'delete_time')
            user_and_group.append(user)
        # 有分组的时候就加入分组条件
        # total_nums = get_total_nums(manager.user_model, is_soft=True, super=UserSuper.COMMON.value)
        total_nums = get_total_nums(manager.user_model, is_soft=True, **condition)

        return user_and_group, total_nums

    def reset_user_password(self, uid, new_password):
        user = find_user(id=uid)
        if user is None:
            raise NotFound(msg='用户不存在')
        with db.auto_commit():
            user.reset_password(new_password)
        return self

    def remove_user(self, uid):
        user = self.get(id=uid)
        if user is None:
            raise NotFound(msg='用户不存在')
        # user.delete(commit=True)
        # 此处我们使用硬删除，一般情况下，推荐使用软删除即，上一行注释的代码
        user.hard_delete(commit=True)
        return self

    def update(self, uid, form):
        user = self.get(id=uid)
        if user is None:
            raise NotFound(msg='用户不存在')
        if user.email != form.email.data:
            exists = self.get(email=form.email.data)
            if exists:
                raise ParameterException(msg='邮箱已被注册，请重新输入邮箱')
        with db.auto_commit():
            user.email = form.email.data
            user.group_id = form.group_id.data
        return self

    def change_status(self, uid, active_or_disable='active'):
        user = self.get(id=uid)
        if user is None:
            raise NotFound(msg='用户不存在')

        active_or_not = UserActive.NOT_ACTIVE.value \
            if active_or_disable == 'active'\
            else UserActive.ACTIVE.value

        if active_or_disable == 'active':
            if not user.is_active:
                raise Forbidden(msg='当前用户已处于禁止状态')

        elif active_or_disable == 'disable':
            if user.is_active:
                raise Forbidden(msg='当前用户已处于激活状态')

        with db.auto_commit():
            user.active = active_or_not

        return self

    def register(self, form):
        user = manager.find_user(nickname=form.nickname.data)
        if user:
            raise RepeatException(msg='用户名重复，请重新输入')
        if form.email.data and form.email.data.strip() != "":
            user = self.query.filter(and_(
                manager.user_model.email.isnot(None),
                manager.user_model.email == form.email.data)
            ).first()
            if user:
                raise RepeatException(msg='注册邮箱重复，请重新输入')
        self._register_user(form)

    def update_info(self, form):
        user = get_current_user()
        if user.email != form.email.data:
            exists = self.get(email=form.email.data)
            if exists:
                raise ParameterException(msg='邮箱已被注册，请重新输入邮箱')
        with db.auto_commit():
            user.email = form.email.data

    @staticmethod
    def get_allowed_apis():
        user = get_current_user()
        auths = db.session.query(
            manager.auth_model.auth, manager.auth_model.module
        ).filter_by(soft=False, group_id=user.group_id).all()
        auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
        from .group import GroupDAO
        res = GroupDAO.split_modules(auths)
        setattr(user, 'auths', res)
        user._fields.append('auths')
        return user

    def _register_user(self, form: RegisterForm):
        with db.auto_commit():
            # 注意：此处使用挂载到manager上的user_model，不可使用默认的User
            user = self
            user.nickname = form.nickname.data
            if form.email.data and form.email.data.strip() != "":
                user.email = form.email.data
            user.password = form.password.data
            user.group_id = form.group_id.data
            db.session.add(user)
