"""
    user apis
    ~~~~~~~~~
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import jsonify
from flask_jwt_extended import create_access_token, jwt_refresh_token_required, get_jwt_identity, get_current_user
from lin.core import manager, route_meta, Log
from lin.db import db
from lin.exception import NotFound, Success, Failed, ParameterException
from lin.jwt import login_required, admin_required, get_tokens
from lin.log import Logger
from lin.redprint import Redprint

from app.dao.auth import AuthDAO
from app.dao.user import UserDAO
from app.validators.forms import LoginForm, RegisterForm, ChangePasswordForm, UpdateInfoForm

user_api = Redprint('user')


@user_api.route('/register', methods=['POST'])
@route_meta(auth='注册', module='用户', mount=False)
@Logger(template='管理员新建了一个用户')  # 记录日志
@admin_required
def register():
    form = RegisterForm().validate_for_api()
    UserDAO().register(form)
    return Success(msg='用户创建成功')


@user_api.route('/login', methods=['POST'])
@route_meta(auth='登陆', module='用户', mount=False)
def login():
    form = LoginForm().validate_for_api()
    user = manager.user_model.verify(form.nickname.data, form.password.data)
    # 此处不能用装饰器记录日志
    Log.create_log(
        message=f'{user.nickname}登陆成功获取了令牌',
        user_id=user.id, user_name=user.nickname,
        status_code=200, method='post',path='/cms/user/login',
        authority='无', commit=True
    )
    access_token, refresh_token = get_tokens(user)
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    })


@user_api.route('/', methods=['PUT'])
@route_meta(auth='用户更新信息', module='用户', mount=False)
@login_required
def update():
    form = UpdateInfoForm().validate_for_api()
    UserDAO().update_info(form)
    return Success(msg='操作成功')


@user_api.route('/change_password', methods=['PUT'])
@route_meta(auth='修改密码', module='用户', mount=False)
@Logger(template='{user.nickname}修改了自己的密码')  # 记录日志
@login_required
def change_password():
    form = ChangePasswordForm().validate_for_api()
    user = get_current_user()
    ok = user.change_password(form.old_password.data, form.new_password.data)
    if ok:
        db.session.commit()
        return Success(msg='密码修改成功')
    else:
        return Failed(msg='修改密码失败')


@user_api.route('/information', methods=['GET'])
@route_meta(auth='查询自己信息', module='用户', mount=False)
@login_required
def get_information():
    current_user = get_current_user()
    return jsonify(current_user)


@user_api.route('/refresh', methods=['GET'])
@route_meta(auth='刷新令牌', module='用户', mount=False)
@jwt_refresh_token_required
def refresh():
    identity = get_jwt_identity()
    if identity:
        access_token = create_access_token(identity=identity)
        return jsonify({
            'access_token': access_token
        })
    return NotFound(msg='refresh_token未被识别')


@user_api.route('/auths', methods=['GET'])
@route_meta(auth='查询自己拥有的权限', module='用户', mount=False)
@login_required
def get_allowed_apis():
    user = UserDAO.get_allowed_apis()
    return jsonify(user)
