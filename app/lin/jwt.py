"""
    jwt(Json Web Token) of Lin
    ~~~~~~~~~

    jwt implement for Lin.

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from functools import wraps

from flask import request
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_current_user,\
    create_access_token, create_refresh_token

from .exception import AuthFailed, InvalidTokenException, ExpiredTokenException, NotFound

jwt = JWTManager()
identity = dict(uid=0, scope='lin')


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_current_user()
        if not current_user.is_admin:
            raise AuthFailed(msg='只有超级管理员可操作')
        return fn(*args, **kwargs)

    return wrapper


def group_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_current_user()
        # check current user is active or not
        # 判断当前用户是否为激活状态
        _check_is_active(current_user)
        # not admin
        if not current_user.is_admin:
            group_id = current_user.group_id
            if group_id is None:
                raise AuthFailed(msg='您还不属于任何权限组，请联系超级管理员获得权限')
            from .core import is_user_allowed
            it = is_user_allowed(group_id)
            if not it:
                raise AuthFailed(msg='权限不够，请联系超级管理员获得权限')
            else:
                return fn(*args, **kwargs)
        else:
            return fn(*args, **kwargs)

    return wrapper


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        _check_is_active(current_user=get_current_user())
        return fn(*args, **kwargs)

    return wrapper


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    from .core import find_user
    if identity['scope'] != 'lin':
        raise AuthFailed()
    if 'remote_addr' in identity.keys() and identity['remote_addr'] != request.remote_addr:
        raise AuthFailed()
    # token is granted , user must be exit
    # 如果token已经被颁发，则该用户一定存在
    user = find_user(id=identity['uid'])
    if user is None:
        raise NotFound(msg='用户不存在')
    return user


@jwt.expired_token_loader
def expired_loader_callback():
    return ExpiredTokenException()


@jwt.invalid_token_loader
def invalid_loader_callback(e):
    return InvalidTokenException()


@jwt.unauthorized_loader
def unauthorized_loader_callback(e):
    return AuthFailed(msg='认证失败，请检查请求头或者重新登陆')


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return {
        'uid': identity['uid'],
        'scope': identity['scope'],
        'remote_addr': identity['remote_addr'] if
        'remote_addr' in identity.keys() else None
    }


def get_tokens(user, verify_remote_addr=False):
    identity['uid'] = user.id
    if verify_remote_addr:
        identity['remote_addr'] = request.remote_addr
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return access_token, refresh_token


def get_access_token(user, scope=None, fresh=False, expires_delta=None, verify_remote_addr=False):
    identity['uid'] = user.id
    identity['scope'] = scope
    if verify_remote_addr:
        identity['remote_addr'] = request.remote_addr
    access_token = create_access_token(
        identity=identity,
        fresh=fresh,
        expires_delta=expires_delta,
    )
    return access_token


def get_refresh_token(user, scope=None, expires_delta=None, verify_remote_addr=False):
    identity['uid'] = user.id
    identity['scope'] = scope
    if verify_remote_addr:
        identity['remote_addr'] = request.remote_addr
    refresh_token = create_refresh_token(
        identity=identity,
        expires_delta=expires_delta
    )
    return refresh_token


def verify_access_token():
    __verify_token('access')


def verify_refresh_token():
    __verify_token('refresh')


def __verify_token(request_type):
    from flask import request
    from flask_jwt_extended.config import config
    from flask_jwt_extended.view_decorators import _decode_jwt_from_cookies as decode
    from flask_jwt_extended.utils import verify_token_claims
    try:
        from flask import _app_ctx_stack as ctx_stack
    except ImportError:
        from flask import _request_ctx_stack as ctx_stack

    if request.method not in config.exempt_methods:
        jwt_data = decode(request_type=request_type)
        ctx_stack.top.jwt = jwt_data
        verify_token_claims(jwt_data)


def _check_is_active(current_user):
    if not current_user.is_active:
        raise AuthFailed(msg='您目前处于未激活状态，请联系超级管理员')
