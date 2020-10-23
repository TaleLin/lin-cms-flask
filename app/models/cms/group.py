from sqlalchemy import func

from app.lin.db import db
from app.lin.interface import InfoCrud


class Group(InfoCrud):
    __tablename__ = 'lin_group'
    __table_args__ = (Index('name_del', 'name', 'delete_time', unique=True), )

    id = Column(Integer(), primary_key=True)
    name = Column(String(60), nullable=False, comment='分组名称，例如：搬砖者')
    info = Column(String(255), comment='分组信息：例如：搬砖的人')
    level = Column(
        SmallInteger(),
        nullable=False,
        server_default=text("3"),
        comment='分组级别 1：root 2：guest 3：user  root（root、guest分组只能存在一个)')

    @classmethod
    def select_by_user_id(cls, user_id) -> list:
        '''
        根据用户Id，通过User-Group关联表，获取所属用户组对象列表
        '''
        from . import User
        from .user_group import UserGroup

        query = db.session.query(UserGroup.group_id).join(
            User,
            User.id == UserGroup.user_id).filter(User.delete_time == None, User.id == user_id)
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        groups = result.all()
        return groups

    @classmethod
    def select_ids_by_user_id(cls, user_id) -> list:
        '''
        根据用户ID，通过User-Group关联表，获取所属用户组的Id列表
        '''
        from . import User
        from .user_group import UserGroup
        query = db.session.query(UserGroup.group_id).join(
            User,
            User.id == UserGroup.user_id).filter(User.delete_time == None, User.id == user_id)
        result = db.session.query(
            cls.id).filter(cls.delete_time == None).filter(cls.id.in_(query))
        # [(1,),(2,),...] => [1,2,...]
        group_ids = [x[0] for x in result.all()]
        return group_ids

    @classmethod
    def count_by_id(cls, id) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.id == id, cls.delete_time == None)
        count = result.scalar()
        return count
