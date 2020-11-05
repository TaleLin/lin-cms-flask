"""
    user apis
    ~~~~~~~~~
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from operator import and_

from app.libs.error_code import RefreshException
from app.lin.core import Log, manager, route_meta
from app.lin.db import db
from app.lin.exception import (Duplicated, Fail, NotFound, ParameterError,
                               Success)
from app.lin.jwt import admin_required, get_tokens, login_required
from app.lin.log import Logger
from app.lin.redprint import Redprint
from app.validators.forms import (AvatarUpdateForm, ChangePasswordForm,
                                  LoginForm, RegisterForm, UpdateInfoForm)
from flask import jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_current_user, get_jwt_identity,
                                verify_jwt_refresh_token_in_request)

user_api = Redprint('user')


@user_api.route('/register', methods=['POST'])
@route_meta(auth='注册', module='用户', mount=False)
@Logger(template='管理员新建了一个用户')  # 记录日志
@admin_required
def register():
    form = RegisterForm().validate_for_api()
    # TODO model更新后开放注释
    # if manager.user_model.count_by_username(form.username.data) > 0:
    #     raise Duplicated(msg='用户名重复，请重新输入')
    # if form.email.data and form.email.data.strip() != "":
    #     if manager.user_model.count_by_email(form.email.data) > 0:
    #         raise Duplicated(msg='注册邮箱重复，请重新输入')
    _register_user(form)
    return Success(msg='用户创建成功')


@ user_api.route('/login', methods=['POST'])
@ route_meta(auth='登录', module='用户', mount=False)
def login():
    form = LoginForm().validate_for_api()
    user = manager.user_model.verify(form.username.data, form.password.data)
    # 此处不能用装饰器记录日志
    Log.create_log(
        message=f'{user.username}登陆成功获取了令牌',
        user_id=user.id, user_name=user.username,
        status_code=200, method='post', path='/cms/user/login',
        authority='无', commit=True
    )
    access_token, refresh_token = get_tokens(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@ user_api.route('', methods=['PUT'])
@ route_meta(auth='用户更新信息', module='用户', mount=False)
@ login_required
def update():
    form = UpdateInfoForm().validate_for_api()
    user = get_current_user()
    if form.email.data and user.email != form.email.data:
        exists = manager.user_model.get(email=form.email.data)
        if exists:
            raise ParameterError(msg='邮箱已被注册，请重新输入邮箱')
    with db.auto_commit():
        user.email = form.email.data
        user.nickname = form.nickname.data
    return Success(msg='操作成功')


@ user_api.route('/change_password', methods=['PUT'])
@ route_meta(auth='修改密码', module='用户', mount=False)
@ Logger(template='{user.username}修改了自己的密码')  # 记录日志
@ login_required
def change_password():
    form = ChangePasswordForm().validate_for_api()
    user = get_current_user()
    ok = user.change_password(form.old_password.data, form.new_password.data)
    if ok:
        db.session.commit()
        return Success(msg='密码修改成功')
    else:
        return Fail(msg='修改密码失败')


@ user_api.route('/information', methods=['GET'])
@ route_meta(auth='查询自己信息', module='用户', mount=False)
@ login_required
def get_information():
    current_user = get_current_user()
    return jsonify(current_user)


@ user_api.route('/refresh', methods=['GET'])
@ route_meta(auth='刷新令牌', module='用户', mount=False)
def refresh():
    try:
        verify_jwt_refresh_token_in_request()
    except Exception:
        return RefreshException()

    identity = get_jwt_identity()
    if identity:
        access_token = create_access_token(identity=identity)
        refresh_token = create_refresh_token(identity=identity)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    return NotFound(msg='refresh_token未被识别')


@ user_api.route('/permissions', methods=['GET'])
@ route_meta(auth='查询自己拥有的权限', module='用户', mount=False)
@ login_required
def get_allowed_apis():
    user = get_current_user()
    auths = db.session.query(
        manager.auth_model.auth, manager.auth_model.module
    ).filter_by(soft=False, group_id=user.group_id).all()
    auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
    from .admin import _split_modules
    res = _split_modules(auths)
    setattr(user, 'auths', res)
    user._fields.append('auths')
    return jsonify(user)


def _register_user(form: RegisterForm):
    with db.auto_commit():
        user = manager.user_model()
        user.username = form.username.data
        if form.email.data and form.email.data.strip() != "":
            user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.flush()
        group_ids = form.group_ids.data
        for group_id in group_ids:
            user_group = manager.user_group_model()
            user_group.user_id = user.id
            user_group.group_id = group_id
            db.session.add(user_group)
