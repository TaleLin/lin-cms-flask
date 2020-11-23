# coding: utf-8
"""
    Some model interfaces of Lin
    ~~~~~~~~~

    interface means you must implement the necessary methods and inherit properties.

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import os
from datetime import datetime

from flask import current_app
from sqlalchemy import (Column, DateTime, FetchedValue, Index, Integer,
                        SmallInteger, String, func, text)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import MixinJSONSerializer, db
from .enums import UserActive, UserAdmin
from .util import camel2line


# 基础的crud model
class BaseCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = []

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 硬删除
    def delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    # 查
    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(
            **kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get('commit') is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get('commit') is True:
            db.session.commit()
        return self


# 提供软删除，及创建时间，更新时间信息的crud model
class InfoCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True),
                         server_default=func.now(), onupdate=func.now())
    delete_time = Column(DateTime(timezone=True))

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, '__tablename__'):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = ['delete_time']

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    # 软删除
    def delete(self, commit=False):
        self.delete_time = datetime.now()
        db.session.add(self)
        # 提交会话
        if commit:
            db.session.commit()

    # 硬删除
    def hard_delete(self, commit=False):
        db.session.delete(self)
        if commit:
            db.session.commit()

    # 查
    @classmethod
    def get(cls, start=None, count=None, one=True, **kwargs):
        # 应用软删除，必须带有delete_time
        if kwargs.get('delete_time') is None:
            kwargs['delete_time'] = None
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(
            **kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(one, '_from', kwargs[key])
            # if key == 'parts':
            #     setattr(one, '_parts', kwargs[key])
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get('commit') is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(self, '_from', kwargs[key])
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get('commit') is True:
            db.session.commit()
        return self

# 调试兼容


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


class ViewModel:
    # 提供自动序列化功能
    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, key):
        return getattr(self, key)
