"""
    admin apis
    ~~~~~~~~~
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import math
from itertools import groupby
from operator import itemgetter

from app.libs.utils import get_page_from_query, paginate
from app.lin import db
from app.lin.core import (find_auth_module, find_user, get_ep_infos, manager,
                          route_meta)
from app.lin.db import get_total_nums
from app.lin.enums import UserActive, UserAdmin
from app.lin.exception import Forbidden, NotFound, ParameterError, Success
from app.lin.jwt import admin_required
from app.lin.log import Logger
from app.lin.redprint import Redprint
from app.validators.forms import (DispatchAuth, DispatchAuths, NewGroup,
                                  RemoveAuths, ResetPasswordForm, UpdateGroup,
                                  UpdateUserInfoForm)
from flask import request

admin_api = Redprint('admin')


@admin_api.route('/permission', methods=['GET'])
@route_meta(auth='查询所有可分配的权限', module='管理员', mount=False)
@admin_required
def authority():
    return get_ep_infos()


@admin_api.route('/users', methods=['GET'])
@route_meta(auth='查询所有用户', module='管理员', mount=False)
@admin_required
def get_admin_users():
    start, count = paginate()
    group_id = request.args.get('group_id')
    group_condition = {'group_id': group_id} if group_id else {}
    user_condition = {'admin': UserAdmin.COMMON.value}
    user_group_list = manager.user_group_model.query.filter_by(
        **group_condition).offset(start).limit(count).all()
    groups = manager.group_model.query.filter_by(
        soft=True, **group_condition).all()
    # 统计符合条件的用户数量 TODO
    total = get_total_nums(manager.user_model, is_soft=True, **group_condition)
    total_page = math.ceil(total / count)
    page = get_page_from_query()
    return {
        "count": count,
        "items": user_group_list,
        "page": page,
        "total": total,
        "total_page": total_page
    }


@admin_api.route('/user/<int:uid>/password', methods=['PUT'])
@route_meta(auth='修改用户密码', module='管理员', mount=False)
@admin_required
def change_user_password(uid):
    form = ResetPasswordForm().validate_for_api()

    user = find_user(id=uid)
    if user is None:
        raise NotFound(msg='用户不存在')

    with db.auto_commit():
        user.reset_password(form.new_password.data)

    return Success(msg='密码修改成功')


@admin_api.route('/user/<int:uid>', methods=['DELETE'])
@route_meta(auth='删除用户', module='管理员', mount=False)
@Logger(template='管理员删除了一个用户')  # 记录日志
@admin_required
def delete_user(uid):
    user = manager.user_model.get(id=uid)
    if user is None:
        raise NotFound(msg='用户不存在')
    # user.delete(commit=True)
    # 此处我们使用硬删除，一般情况下，推荐使用软删除即，上一行注释的代码
    user.hard_delete(commit=True)
    return Success(msg='操作成功')


@admin_api.route('/user/<int:uid>', methods=['PUT'])
@route_meta(auth='管理员更新用户信息', module='管理员', mount=False)
@admin_required
def update_user(uid):
    form = UpdateUserInfoForm().validate_for_api()

    user = manager.user_model.get(id=uid)
    if user is None:
        raise NotFound(msg='用户不存在')
    if user.email != form.email.data:
        exists = manager.user_model.get(email=form.email.data)
        if exists:
            raise ParameterError(msg='邮箱已被注册，请重新输入邮箱')
    with db.auto_commit():
        user.email = form.email.data
        user.group_id = form.group_id.data
    return Success(msg='操作成功')


@admin_api.route('/group', methods=['GET'])
@route_meta(auth='查询所有权限组及其权限', module='管理员', mount=False)
@admin_required
def get_admin_groups():
    start, count = paginate()
    groups = manager.group_model.query.filter().offset(
        start).limit(count).all()
    if groups is None:
        raise NotFound(msg='不存在任何权限组')

    for group in groups:
        auths = db.session.query(
            manager.auth_model.auth, manager.auth_model.module
        ).filter_by(soft=False, group_id=group.id).all()

        auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
        res = _split_modules(auths)
        setattr(group, 'auths', res)
        group._fields.append('auths')

    total = get_total_nums(manager.group_model)
    total_page = math.ceil(total / count)
    page = get_page_from_query()

    return {
        "count": count,
        "items": groups,
        "page": page,
        "total": total,
        "total_page": total_page
    }


@admin_api.route('/group/all', methods=['GET'])
@route_meta(auth='查询所有权限组', module='管理员', mount=False)
@admin_required
def get_all_group():
    groups = manager.group_model.get(one=False)
    if groups is None:
        raise NotFound(msg='不存在任何权限组')
    return groups


@admin_api.route('/group/<int:gid>', methods=['GET'])
@route_meta(auth='查询一个权限组及其权限', module='管理员', mount=False)
@admin_required
def get_group(gid):
    group = manager.group_model.get(id=gid, one=True, soft=False)
    if group is None:
        raise NotFound(msg='分组不存在')
    auths = db.session.query(
        manager.auth_model.auth, manager.auth_model.module
    ).filter_by(soft=False, group_id=group.id).all()
    auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
    res = _split_modules(auths)
    setattr(group, 'auths', res)
    group._fields.append('auths')
    return group


@admin_api.route('/group', methods=['POST'])
@route_meta(auth='新建权限组', module='管理员', mount=False)
@Logger(template='管理员新建了一个权限组')  # 记录日志
@admin_required
def create_group():
    form = NewGroup().validate_for_api()
    exists = manager.group_model.get(name=form.name.data)
    if exists:
        raise Forbidden(msg='分组已存在，不可创建同名分组')
    with db.auto_commit():
        group = manager.group_model.create(
            name=form.name.data,
            info=form.info.data,
        )
        db.session.flush()
        for permission_id in form.permission_ids.data:
            manager.group_permission_model.create(
                group_id=group.id,
                permission_id=permission_id
            )

    return Success(msg='新建分组成功')


@admin_api.route('/group/<int:gid>', methods=['PUT'])
@route_meta(auth='更新一个权限组', module='管理员', mount=False)
@admin_required
def update_group(gid):
    form = UpdateGroup().validate_for_api()
    exists = manager.group_model.get(id=gid)
    if not exists:
        raise NotFound(msg='分组不存在，更新失败')
    exists.update(name=form.name.data, info=form.info.data, commit=True)
    return Success(msg='更新分组成功')


@admin_api.route('/group/<int:gid>', methods=['DELETE'])
@route_meta(auth='删除一个权限组', module='管理员', mount=False)
@Logger(template='管理员删除一个权限组')  # 记录日志
@admin_required
def delete_group(gid):
    exist = manager.group_model.get(id=gid)
    if not exist:
        raise NotFound(msg='分组不存在，删除失败')
    if manager.user_model.get(group_id=gid):
        raise Forbidden(msg='分组下存在用户，不可删除')
    # 删除group拥有的权限
    manager.auth_model.query.filter(
        manager.auth_model.group_id == gid).delete()
    exist.delete(commit=True)
    return Success(msg='删除分组成功')


@admin_api.route('/permission/dispatch', methods=['POST'])
@route_meta(auth='分配单个权限', module='管理员', mount=False)
@admin_required
def dispatch_auth():
    form = DispatchAuth().validate_for_api()
    one = manager.auth_model.get(
        group_id=form.group_id.data, auth=form.auth.data)
    if one:
        raise Forbidden(msg='已有权限，不可重复添加')
    meta = find_auth_module(form.auth.data)
    manager.auth_model.create(
        group_id=form.group_id.data,
        auth=meta.auth,
        module=meta.module,
        commit=True
    )
    return Success(msg='添加权限成功')


@admin_api.route('/permission/dispatch/batch', methods=['POST'])
@route_meta(auth='分配多个权限', module='管理员', mount=False)
@admin_required
def dispatch_auths():
    form = DispatchAuths().validate_for_api()
    with db.auto_commit():
        for auth in form.auths.data:
            one = manager.auth_model.get(
                group_id=form.group_id.data, auth=auth)
            if not one:
                meta = find_auth_module(auth)
                manager.auth_model.create(
                    group_id=form.group_id.data,
                    auth=meta.auth,
                    module=meta.module
                )
    return Success(msg='添加权限成功')


@admin_api.route('/permission/remove', methods=['POST'])
@route_meta(auth='删除多个权限', module='管理员', mount=False)
@admin_required
def remove_auths():
    form = RemoveAuths().validate_for_api()

    with db.auto_commit():
        db.session.query(manager.auth_model).filter(
            manager.auth_model.auth.in_(form.auths.data),
            manager.auth_model.group_id == form.group_id.data
        ).delete(synchronize_session=False)

    return Success(msg='删除权限成功')


def _split_modules(auths):
    auths.sort(key=itemgetter('module'))
    tmps = groupby(auths, itemgetter('module'))
    res = []
    for key, group in tmps:
        res.append({key: list(group)})
    return res


def _change_status(uid, active_or_disable='active'):
    user = manager.user_model.get(id=uid)
    if user is None:
        raise NotFound(msg='用户不存在')

    active_or_not = UserActive.NOT_ACTIVE.value \
        if active_or_disable == 'active' \
        else UserActive.ACTIVE.value

    if active_or_disable == 'active':
        if not user.is_active:
            raise Forbidden(msg='当前用户已处于禁止状态')

    elif active_or_disable == 'disable':
        if user.is_active:
            raise Forbidden(msg='当前用户已处于激活状态')

    with db.auto_commit():
        user.active = active_or_not
