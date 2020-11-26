# from app.lin.model.user import User as LinUser


# class User(LinUser):
#     pass
import os
from datetime import datetime

from app.lin import manager, db
from app.lin.enums import UserActive, UserAdmin
from app.lin.utils import camel2line
from flask import current_app
from sqlalchemy import (Column, DateTime, FetchedValue, Index, Integer,
                        SmallInteger, String, func, text)
from werkzeug.security import check_password_hash, generate_password_hash
from app.lin.interface import InfoCrud


class UserInterface(InfoCrud):
    __tablename__ = 'lin_user'

    id = Column(Integer, primary_key=True)
    username = Column(String(24), nullable=False, unique=True, comment='用户名')
    nickname = Column(String(24), unique=True, default=None, comment='昵称')
    _avatar = Column('avatar', String(255), comment='头像url')
    # : admin express the user is admin(admin) ;  1 -> common |  2 -> admin
    # : admin 代表是否为超级管理员 ;  1 -> 普通用户 |  2 -> 超级管理员
    admin = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue(),
                   comment='是否为超级管理员 ;  1 -> 普通用户 |  2 -> 超级管理员')
    # : active express the user can manage the authorities or not ; 1 -> active | 2 -> not
    # : active 代表当前用户是否为激活状态，非激活状态默认失去用户权限 ; 1 -> 激活 | 2 -> 非激活
    active = Column(SmallInteger, nullable=False, default=1, server_default=FetchedValue(),
                    comment='当前用户是否为激活状态，非激活状态默认失去用户权限 ; 1 -> 激活 | 2 -> 非激活')
    # : used to send email in the future
    # : 预留字段，方便以后扩展
    email = Column(String(100), unique=True, comment='电子邮箱')
    # : which group the user belongs,nullable is true
    # : 用户所属的分组id
    group_id = Column(Integer, comment='用户所属的分组id')
    _password = Column('password', String(100), comment='密码')

    def _set_fields(self):
        self._exclude = ['password', 'delete_time']

    @property
    def avatar(self):
        site_domain = current_app.config.get('SITE_DOMAIN') if current_app.config.get(
            'SITE_DOMAIN') else "http://127.0.0.1:5000"
        if self._avatar is not None:
            return site_domain + os.path.join(current_app.static_url_path, self._avatar)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    @property
    def is_admin(self):
        return self.admin == UserAdmin.ADMIN.value

    @property
    def is_active(self):
        return self.active == UserActive.ACTIVE.value

    @classmethod
    def verify(cls, username, password):
        raise Exception('must implement this method')

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)

    def reset_password(self, new_password):
        raise Exception('must implement this method')

    def change_password(self, old_password, new_password):
        raise Exception('must implement this method')


class User(UserInterface, db.Model):

    @classmethod
    def verify(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user is None or user.delete_time is not None:
            raise NotFound('用户不存在')
        if not user.check_password(password):
            raise ParameterError('密码错误，请输入正确密码')
        if not user.is_active:
            raise UnAuthentication('您目前处于未激活状态，请联系超级管理员')
        return user

    def reset_password(self, new_password):
        #: attention,remember to commit
        #: 注意，修改密码后记得提交至数据库
        self.password = new_password

    def change_password(self, old_password, new_password):
        #: attention,remember to commit
        #: 注意，修改密码后记得提交至数据库
        if self.check_password(old_password):
            self.password = new_password
            return True
        return False

    @classmethod
    def select_page_by_group_id(cls, group_id, root_group_id) -> list:
        '''
        通过分组id分页获取用户数据
        '''
        query = db.session.query(manager.user_group_model.user_id).filter(
            manager.user_group_model.group_id == group_id,
            manager.user_group_model.group_id != root_group_id)
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        users = result.all()
        return users
