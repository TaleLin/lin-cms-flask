"""
    admin apis
    ~~~~~~~~~
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from itertools import groupby
from operator import itemgetter

from flask import jsonify
from lin.core import get_ep_infos, route_meta
from lin.exception import Success
from lin.jwt import admin_required
from lin.log import Logger
from lin.redprint import Redprint

from app.dao.auth import AuthDAO
from app.dao.group import GroupDAO
from app.dao.user import UserDAO
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
    user_and_group, total_nums = UserDAO().get_all()
    return jsonify({
        "collection": user_and_group,
        'total_nums': total_nums
    })


@admin_api.route('/password/<int:uid>', methods=['PUT'])
@route_meta(auth='修改用户密码', module='管理员', mount=False)
@admin_required
def change_user_password(uid):
    form = ResetPasswordForm().validate_for_api()
    UserDAO().reset_user_password(uid, form.new_password.data)
    return Success(msg='密码修改成功')


@admin_api.route('/<int:uid>', methods=['DELETE'])
@route_meta(auth='删除用户', module='管理员', mount=False)
@Logger(template='管理员删除了一个用户')  # 记录日志
@admin_required
def delete_user(uid):
    UserDAO().remove_user(uid)
    return Success(msg='操作成功')


@admin_api.route('/<int:uid>', methods=['PUT'])
@route_meta(auth='管理员更新用户信息', module='管理员', mount=False)
@admin_required
def update_user(uid):
    form = UpdateUserInfoForm().validate_for_api()
    UserDAO().update(uid, form)
    return Success(msg='操作成功')


@admin_api.route('/disable/<int:uid>', methods=['PUT'])
@route_meta(auth='禁用用户', module='管理员', mount=False)
@admin_required
def trans2disable(uid):
    UserDAO().change_status(uid, 'active')
    return Success(msg='操作成功')


@admin_api.route('/active/<int:uid>', methods=['PUT'])
@route_meta(auth='激活用户', module='管理员', mount=False)
@admin_required
def trans2active(uid):
    UserDAO().change_status(uid, 'disable')
    return Success(msg='操作成功')


@admin_api.route('/groups', methods=['GET'])
@route_meta(auth='查询所有权限组及其权限', module='管理员', mount=False)
@admin_required
def get_admin_groups():
    groups_info, total_nums = GroupDAO().get_groups_info()

    return jsonify({
        "collection": groups_info,
        'total_nums': total_nums
    })


@admin_api.route('/group/all', methods=['GET'])
@route_meta(auth='查询所有权限组', module='管理员', mount=False)
@admin_required
def get_all_group():
    groups = GroupDAO().get_all()
    return jsonify(groups)


@admin_api.route('/group/<int:gid>', methods=['GET'])
@route_meta(auth='查询一个权限组及其权限', module='管理员', mount=False)
@admin_required
def get_group(gid):
    group = GroupDAO().get_single_info(gid)
    return jsonify(group)


@admin_api.route('/group', methods=['POST'])
@route_meta(auth='新建权限组', module='管理员', mount=False)
@Logger(template='管理员新建了一个权限组')  # 记录日志
@admin_required
def create_group():
    form = NewGroup().validate_for_api()
    GroupDAO().new_group(form)
    return Success(msg='新建分组成功')


@admin_api.route('/group/<int:gid>', methods=['PUT'])
@route_meta(auth='更新一个权限组', module='管理员', mount=False)
@admin_required
def update_group(gid):
    form = UpdateGroup().validate_for_api()
    GroupDAO().update_group(gid, form)
    return Success(msg='更新分组成功')


@admin_api.route('/group/<int:gid>', methods=['DELETE'])
@route_meta(auth='删除一个权限组', module='管理员', mount=False)
@Logger(template='管理员删除一个权限组')  # 记录日志
@admin_required
def delete_group(gid):
    GroupDAO().remove_group(gid)
    return Success(msg='删除分组成功')


@admin_api.route('/dispatch', methods=['POST'])
@route_meta(auth='分配单个权限', module='管理员', mount=False)
@admin_required
def dispatch_auth():
    form = DispatchAuth().validate_for_api()
    AuthDAO().patch_one(form)
    return Success(msg='添加权限成功')


@admin_api.route('/dispatch/patch', methods=['POST'])
@route_meta(auth='分配多个权限', module='管理员', mount=False)
@admin_required
def dispatch_auths():
    form = DispatchAuths().validate_for_api()
    AuthDAO().patch_all(form)
    return Success(msg='添加权限成功')


@admin_api.route('/remove', methods=['POST'])
@route_meta(auth='删除多个权限', module='管理员', mount=False)
@admin_required
def remove_auths():
    form = RemoveAuths().validate_for_api()
    AuthDAO().remove_auths(form)
    return Success(msg='删除权限成功')


def _split_modules(auths):
    auths.sort(key=itemgetter('module'))
    tmps = groupby(auths, itemgetter('module'))
    res = []
    for key, group in tmps:
        res.append({key: list(group)})
    return res

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
