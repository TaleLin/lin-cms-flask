# coding: utf-8
"""
    Some model interfaces of Lin
    ~~~~~~~~~

    interface means you must implement the necessary methods and inherit properties.

    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import os
from datetime import datetime

from flask import current_app
from sqlalchemy import Column, DateTime, func, text
from werkzeug.security import check_password_hash, generate_password_hash

from .db import MixinJSONSerializer, db
from .utils import camel2line


# 基础的crud model
class BaseCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, "__tablename__"):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = []

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != "id":
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
        return cls.query.filter().filter_by(**kwargs).offset(start).limit(count).all()

    # 增
    @classmethod
    def create(cls, **kwargs):
        one = cls()
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        db.session.add(one)
        if kwargs.get("commit") is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get("commit") is True:
            db.session.commit()
        return self


# 提供软删除，及创建时间，更新时间信息的crud model
class InfoCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    delete_time = Column(DateTime(timezone=True))

    def __init__(self):
        name: str = self.__class__.__name__
        if not hasattr(self, "__tablename__"):
            self.__tablename__ = camel2line(name)

    def _set_fields(self):
        self._exclude = ["delete_time"]

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != "id":
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
        if kwargs.get("delete_time") is None:
            kwargs["delete_time"] = None
        if one:
            return cls.query.filter().filter_by(**kwargs).first()
        return cls.query.filter().filter_by(**kwargs).offset(start).limit(count).all()

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
        if kwargs.get("commit") is True:
            db.session.commit()
        return one

    def update(self, **kwargs):
        for key in kwargs.keys():
            # if key == 'from':
            #     setattr(self, '_from', kwargs[key])
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        db.session.add(self)
        if kwargs.get("commit") is True:
            db.session.commit()
        return self


class LinViewModel:
    # 提供自动序列化功能
    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, key):
        return getattr(self, key)
