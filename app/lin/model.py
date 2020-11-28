import os

from app.lin.core import manager
from app.lin.db import db
from app.lin.enums import GroupLevelEnum
from app.lin.interface import BaseCrud, InfoCrud
from flask import current_app
from sqlalchemy import Column, Index, Integer, SmallInteger, String, func, text
from werkzeug.security import check_password_hash, generate_password_hash

from .exception import NotFound, ParameterError, UnAuthentication


class Group(InfoCrud):
    __tablename__ = "lin_group"
    __table_args__ = (Index("name_del", "name", "delete_time", unique=True),)

    id = Column(Integer(), primary_key=True)
    name = Column(String(60), nullable=False, comment="分组名称，例如：搬砖者")
    info = Column(String(255), comment="分组信息：例如：搬砖的人")
    level = Column(
        SmallInteger(),
        nullable=False,
        server_default=text(str(GroupLevelEnum.USER.value)),
        comment="分组级别 1：ROOT 2：GUEST 3：USER （ROOT、GUEST Level 对应分组均唯一存在)",
    )

    def _set_fields(self):
        self._exclude = ["delete_time", "create_time", "update_time"]

    @classmethod
    def count_by_id(cls, id) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.id == id, cls.delete_time == None
        )
        count = result.scalar()
        return count


class GroupPermission(BaseCrud):
    __tablename__ = "lin_group_permission"
    __table_args__ = (Index("group_id_permission_id", "group_id", "permission_id"),)

    id = Column(Integer(), primary_key=True)
    group_id = Column(Integer(), nullable=False, comment="分组id")
    permission_id = Column(Integer(), nullable=False, comment="权限id")


class Permission(InfoCrud):
    __tablename__ = "lin_permission"

    id = Column(Integer(), primary_key=True)
    name = Column(String(60), nullable=False, comment="权限名称，例如：访问首页")
    module = Column(String(50), nullable=False, comment="权限所属模块，例如：人员管理")
    mount = Column(
        SmallInteger(), nullable=False, server_default=text("1"), comment="0：关闭 1：开启"
    )

    @classmethod
    def exist_by_group_ids_and_module_and_name(
        cls, group_ids: list, module, name
    ) -> bool:
        """
        传入用户组的 id 列表 和 权限模块名称 权限名称，根据 Group-Permission关联表 判断对应权限是否存在
        """
        query = db.session.query(manager.group_permission_model.permission_id).filter(
            manager.group_permission_model.group_id.in_(group_ids)
        )
        result = cls.query.filter_by(
            soft=True, module=module, name=name, mount=True
        ).filter(cls.id.in_(query))
        permission = result.first()
        return True if permission else False


class User(InfoCrud):
    __tablename__ = "lin_user"
    __table_args__ = (
        Index("username_del", "username", "delete_time", unique=True),
        Index("email_del", "email", "delete_time", unique=True),
    )

    id = Column(Integer(), primary_key=True)
    username = Column(String(24), nullable=False, comment="用户名，唯一")
    nickname = Column(String(24), comment="用户昵称")
    _avatar = Column("avatar", String(500), comment="头像url")
    email = Column(String(100), comment="邮箱")

    def _set_fields(self):
        self._exclude = ["delete_time", "create_time", "update_time"]

    @property
    def avatar(self):
        site_domain = (
            current_app.config.get("SITE_DOMAIN")
            if current_app.config.get("SITE_DOMAIN")
            else "http://127.0.0.1:5000"
        )
        if self._avatar is not None:
            return site_domain + os.path.join(current_app.static_url_path, self._avatar)

    @classmethod
    def count_by_id(cls, uid) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.id == uid, cls.delete_time == None
        )
        count = result.scalar()
        return count

    @staticmethod
    def count_by_id_and_group_name(user_id, group_name) -> int:
        stmt = (
            db.session.query(manager.group_model.id.label("group_id"))
            .filter_by(soft=True, name=group_name)
            .subquery()
        )
        result = db.session.query(func.count(manager.user_group_model.id)).filter(
            manager.user_group_model.user_id == user_id,
            manager.user_group_model.group_id == stmt.c.group_id,
        )
        count = result.scalar()
        return count

    @property
    def is_admin(self):
        return (
            manager.user_group_model.get(user_id=self.id).group_id
            == GroupLevelEnum.ROOT.value
        )

    @property
    def is_active(self):
        return True

    @property
    def password(self):
        return manager.identity_model.get(user_id=self.id).credential

    @password.setter
    def password(self, raw):
        user_identity = manager.identity_model.get(user_id=self.id)
        if user_identity:
            user_identity.credential = generate_password_hash(raw)
            user_identity.update(synchronize_session=False)
        else:
            user_identity = manager.identity_model()
            user_identity.user_id = self.id
            user_identity.identity_type = "USERNAME_PASSWORD"
            user_identity.identity = "root"
            user_identity.credential = generate_password_hash(raw)
            db.session.add(user_identity)

    def check_password(self, raw):
        return check_password_hash(self.password, raw)

    @classmethod
    def verify(cls, username, password):
        user = cls.query.filter_by(username=username).first()
        if user is None or user.delete_time is not None:
            raise NotFound("用户不存在")
        if not user.check_password(password):
            raise ParameterError("密码错误，请输入正确密码")
        if not user.is_active:
            raise UnAuthentication("您目前处于未激活状态，请联系超级管理员")
        return user


class UserGroup(BaseCrud):
    __tablename__ = "lin_user_group"
    __table_args__ = (Index("user_id_group_id", "user_id", "group_id"),)

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, comment="用户id")
    group_id = Column(Integer(), nullable=False, comment="分组id")


class UserIdentity(InfoCrud):
    __tablename__ = "lin_user_identity"

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, comment="用户id")
    identity_type = Column(String(100), nullable=False, comment="认证类型")
    identifier = Column(String(100), comment="标识")
    credential = Column(String(100), comment="凭证")
