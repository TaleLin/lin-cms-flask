"""
    admin apis
    ~~~~~~~~~
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from itertools import groupby
from operator import itemgetter

from flask import jsonify, request
from lin.log import Logger

from lin.redprint import Redprint
from lin.core import get_ep_infos, manager, find_auth_module, route_meta, find_user
from lin.jwt import admin_required
from lin.util import paginate
from lin.db import db, get_total_nums
from lin.enums import UserSuper, UserActive
from lin.exception import NotFound, Forbidden, Success, ParameterException

from app.validators.forms import NewGroup, DispatchAuth, DispatchAuths, RemoveAuths, UpdateGroup, ResetPasswordForm, \
    UpdateUserInfoForm

admin_api = Redprint('admin')


@admin_api.route('/authority', methods=['GET'])
@route_meta(auth='查询所有可分配的权限', module='管理员', mount=False)
@admin_required
def authority():
    return jsonify(get_ep_infos())


@admin_api.route('/users', methods=['GET'])
@route_meta(auth='查询所有用户', module='管理员', mount=False)
@admin_required
def get_admin_users():
    start, count = paginate()
    group_id = request.args.get('group_id')
    condition = {'super': UserSuper.COMMON.value, 'group_id': group_id} if group_id else {
        'super': UserSuper.COMMON.value}
    users = db.session.query(manager.user_model, manager.group_model.name) \
        .filter_by(**condition) \
        .join(manager.group_model, manager.user_model.group_id == manager.group_model.id) \
        .offset(start).limit(count).all()
    user_and_group = []
    for user, group_name in users:
        setattr(user, 'group_name', group_name)
        user._fields.append('group_name')
        user.hide('update_time', 'delete_time')
        user_and_group.append(user)
    # 有分组的时候就加入分组条件
    # total_nums = get_total_nums(manager.user_model, is_soft=True, super=UserSuper.COMMON.value)
    total_nums = get_total_nums(manager.user_model, is_soft=True, **condition)
    return jsonify({
        "collection": user_and_group,
        # 超级管理员不算入总数
        'total_nums': total_nums
    })


@admin_api.route('/password/<int:id>', methods=['PUT'])
@route_meta(auth='修改用户密码', module='管理员', mount=False)
@admin_required
def change_user_password(id):
    form = ResetPasswordForm().validate_for_api()
    user = find_user(id=id)
    if user is None:
        raise NotFound(msg='用户不存在')
    with db.auto_commit():
        user.reset_password(form.new_password.data)
    return Success(msg='密码修改成功')


@admin_api.route('/<int:id>', methods=['DELETE'])
@route_meta(auth='删除用户', module='管理员', mount=False)
@Logger(template='管理员删除了一个用户')  # 记录日志
@admin_required
def delete_user(id):
    user = manager.user_model.get(id=id)
    if user is None:
        raise NotFound(msg='用户不存在')
    # user.delete(commit=True)
    # 此处我们使用硬删除，一般情况下，推荐使用软删除即，上一行注释的代码
    user.hard_delete(commit=True)
    return Success(msg='操作成功')


@admin_api.route('/<int:id>', methods=['PUT'])
@route_meta(auth='管理员更新用户信息', module='管理员', mount=False)
@admin_required
def update_user(id):
    form = UpdateUserInfoForm().validate_for_api()
    user = manager.user_model.get(id=id)
    if user is None:
        raise NotFound(msg='用户不存在')
    if user.email != form.email.data:
        exit = manager.user_model.get(email=form.email.data)
        if exit:
            raise ParameterException(msg='邮箱已被注册，请重新输入邮箱')
    with db.auto_commit():
        user.email = form.email.data
        user.group_id = form.group_id.data
    return Success(msg='操作成功')


@admin_api.route('/disable/<int:id>', methods=['PUT'])
@route_meta(auth='禁用用户', module='管理员', mount=False)
@admin_required
def trans2disable(id):
    user = manager.user_model.get(id=id)
    if user is None:
        raise NotFound(msg='用户不存在')
    if not user.is_active:
        raise Forbidden(msg='当前用户已处于禁止状态')
    with db.auto_commit():
        user.active = UserActive.NOT_ACTIVE.value
    return Success(msg='操作成功')


@admin_api.route('/active/<int:id>', methods=['PUT'])
@route_meta(auth='激活用户', module='管理员', mount=False)
@admin_required
def trans2active(id):
    user = manager.user_model.get(id=id)
    if user is None:
        raise NotFound(msg='用户不存在')
    if user.is_active:
        raise Forbidden(msg='当前用户已处于激活状态')
    with db.auto_commit():
        user.active = UserActive.ACTIVE.value
    return Success(msg='操作成功')


@admin_api.route('/groups', methods=['GET'])
@route_meta(auth='查询所有权限组及其权限', module='管理员', mount=False)
@admin_required
def get_admin_groups():
    start, count = paginate()
    groups = manager.group_model.query.filter().offset(start).limit(count).all()
    if groups is None:
        raise NotFound(msg='不存在任何权限组')
    for group in groups:
        auths = db.session.query(manager.auth_model.auth, manager.auth_model.module) \
            .filter_by(soft=False, group_id=group.id).all()
        auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
        res = _split_modules(auths)
        setattr(group, 'auths', res)
        group._fields.append('auths')
    total_nums = get_total_nums(manager.group_model)
    return jsonify({
        "collection": groups,
        'total_nums': total_nums
    })


def _split_modules(auths):
    auths.sort(key=itemgetter('module'))
    tmps = groupby(auths, itemgetter('module'))
    res = []
    for key, group in tmps:
        res.append({key: list(group)})
    return res


@admin_api.route('/group/all', methods=['GET'])
@route_meta(auth='查询所有权限组', module='管理员', mount=False)
@admin_required
def get_all_group():
    groups = manager.group_model.get(one=False)
    if groups is None:
        raise NotFound(msg='不存在任何权限组')
    return jsonify(groups)


@admin_api.route('/group/<int:id>', methods=['GET'])
@route_meta(auth='查询一个权限组及其权限', module='管理员', mount=False)
@admin_required
def get_group(id):
    group = manager.group_model.get(id=id, one=True, soft=False)
    if group is None:
        raise NotFound(msg='分组不存在')
    auths = db.session.query(manager.auth_model.auth, manager.auth_model.module) \
        .filter_by(soft=False, group_id=group.id).all()
    auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
    res = _split_modules(auths)
    setattr(group, 'auths', res)
    group._fields.append('auths')
    return jsonify(group)


@admin_api.route('/group', methods=['POST'])
@route_meta(auth='新建权限组', module='管理员', mount=False)
@Logger(template='管理员新建了一个权限组')  # 记录日志
@admin_required
def create_group():
    form = NewGroup().validate_for_api()
    exist = manager.group_model.get(name=form.name.data)
    if exist:
        raise Forbidden(msg='分组已存在，不可创建同名分组')
    with db.auto_commit():
        group = manager.group_model.create(name=form.name.data, info=form.info.data)
        db.session.flush()
        for auth in form.auths.data:
            meta = find_auth_module(auth)
            if meta:
                manager.auth_model.create(auth=meta.auth, module=meta.module, group_id=group.id)
    return Success(msg='新建分组成功')


@admin_api.route('/group/<int:id>', methods=['PUT'])
@route_meta(auth='更新一个权限组', module='管理员', mount=False)
@admin_required
def update_group(id):
    form = UpdateGroup().validate_for_api()
    exist = manager.group_model.get(id=id)
    if not exist:
        raise NotFound(msg='分组不存在，更新失败')
    exist.update(name=form.name.data, info=form.info.data, commit=True)
    return Success(msg='更新分组成功')


@admin_api.route('/group/<int:id>', methods=['DELETE'])
@route_meta(auth='删除一个权限组', module='管理员', mount=False)
@Logger(template='管理员删除一个权限组')  # 记录日志
@admin_required
def delete_group(id):
    exist = manager.group_model.get(id=id)
    if not exist:
        raise NotFound(msg='分组不存在，删除失败')
    if manager.user_model.get(group_id=id):
        raise Forbidden(msg='分组下存在用户，不可删除')
    # 删除group拥有的权限
    db.session.query(manager.auth_model).filter(manager.auth_model.group_id == id).delete()
    exist.delete(commit=True)
    return Success(msg='删除分组成功')


@admin_api.route('/dispatch', methods=['POST'])
@route_meta(auth='分配单个权限', module='管理员', mount=False)
@admin_required
def dispatch_auth():
    form = DispatchAuth()
    form.validate_for_api()
    one = manager.auth_model.get(group_id=form.group_id.data, auth=form.auth.data)
    if one:
        raise Forbidden(msg='已有权限，不可重复添加')
    meta = find_auth_module(form.auth.data)
    manager.auth_model.create(group_id=form.group_id.data, auth=meta.auth, module=meta.module, commit=True)
    return Success(msg='添加权限成功')


@admin_api.route('/dispatch/patch', methods=['POST'])
@route_meta(auth='分配多个权限', module='管理员', mount=False)
@admin_required
def dispatch_auths():
    form = DispatchAuths()
    form.validate_for_api()
    with db.auto_commit():
        for auth in form.auths.data:
            one = manager.auth_model.get(group_id=form.group_id.data, auth=auth)
            if not one:
                meta = find_auth_module(auth)
                manager.auth_model.create(group_id=form.group_id.data, auth=meta.auth, module=meta.module)
    return Success(msg='添加权限成功')


@admin_api.route('/remove', methods=['POST'])
@route_meta(auth='删除多个权限', module='管理员', mount=False)
@admin_required
def remove_auths():
    form = RemoveAuths().validate_for_api()
    with db.auto_commit():
        db.session.query(manager.auth_model) \
            .filter(manager.auth_model.auth.in_(form.auths.data),
                    manager.auth_model.group_id == form.group_id.data) \
            .delete(synchronize_session=False)
    return Success(msg='删除权限成功')

# --------------------------------------------------
# --------------------Abandon-----------------------
# --------------------------------------------------
# --------------------------------------------------
# @admin_api.route('/auth', methods=['PUT'])
# @route_meta(auth='更新权限', module='管理员', mount=False)
# @admin_required
# def update_auths():
#     form = DispatchAuths().validate_for_api()
#     # 查询分组所拥有的权限
#     haved_auths = db.session.query(manager.auth_model) \
#         .filter(manager.auth_model.group_id == form.group_id.data) \
#         .all()
#     will_add_auths, will_remove_auths = _diff_auths(form.auths.data, haved_auths)
#
#     with db.auto_commit():
#         for auth in will_add_auths:
#             meta = find_auth_module(auth)
#             manager.auth_model.create(group_id=form.group_id.data, auth=meta.auth, module=meta.module)
#
#         db.session.query(manager.auth_model) \
#             .filter(manager.auth_model.auth.in_(will_remove_auths),
#                     manager.auth_model.group_id == form.group_id.data) \
#             .delete(synchronize_session=False)
#     return Success(msg='更新权限成功')
#
#
# def _diff_auths(request_auths, haved_auths):
#     # 待删除权限，在发送来的权限中不存在拥有的权限即删除
#     will_remove_auths = []
#     for haved_auth in haved_auths:
#         tmp_auth = haved_auth.auth
#         if tmp_auth not in request_auths:
#             will_remove_auths.append(tmp_auth)
#
#     # 找新增的权限
#     # 在已有的权限中不存在发送的权限
#     will_add_auths = []
#     haved_tmps = [haved_auth.auth for haved_auth in haved_auths]
#     for request_auth in request_auths:
#         if request_auth not in haved_tmps:
#             will_add_auths.append(request_auth)
#
#     return will_add_auths, will_remove_auths

# 废除
# @admin_api.route('/api_groups', methods=['GET'])
# @admin_required
# def get_apis_with_group():
#     apis = db.session.query(manager.auth_model.id, manager.auth_model.auth, manager.auth_model.module) \
#         .filter_by().all()
#     apis = [{'id': api[0], 'auth': api[1], 'module': api[2]} for api in apis]
#     res = _split_modules(apis)
#     return jsonify(res)
