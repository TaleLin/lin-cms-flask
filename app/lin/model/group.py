import os

from app.lin import db, manager
from app.lin.enums import GroupLevel
from app.lin.interface import InfoCrud
from sqlalchemy import Column, Index, Integer, SmallInteger, String, func, text


class Group(InfoCrud):
    __tablename__ = 'lin_group'
    __table_args__ = (Index('name_del', 'name', 'delete_time', unique=True), )

    id = Column(Integer(), primary_key=True)
    name = Column(String(60), nullable=False, comment='分组名称，例如：搬砖者')
    info = Column(String(255), comment='分组信息：例如：搬砖的人')
    level = Column(
        SmallInteger(),
        nullable=False,
        server_default=text(str(GroupLevel.USER.value)),
        comment='分组级别 1：ROOT 2：GUEST 3：USER （ROOT、GUEST Level 对应分组均唯一存在)')

    @ classmethod
    def select_by_user_id(cls, user_id) -> list:
        '''
        根据用户Id，通过User-Group关联表，获取所属用户组对象列表
        '''
        query = db.session.query(manager.user_group_model.group_id).join(
            manager.user_model,
            manager.user_model.id == manager.user_group_model.user_id).filter(manager.user_model.delete_time == None, manager.user_model.id == user_id)
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        groups = result.all()
        return groups

    @ classmethod
    def select_ids_by_user_id(cls, user_id) -> list:
        '''
        根据用户ID，通过User-Group关联表，获取所属用户组的Id列表
        '''
        query = db.session.query(manager.user_group_model.group_id).join(
            manager.user_model,
            manager.user_model.id == manager.user_group_model.user_id).filter(
            manager.user_model.delete_time == None,
            manager.user_model.id == user_id)
        result = db.session.query(
            cls.id).filter(cls.delete_time == None).filter(cls.id.in_(query))
        # [(1,),(2,),...] => [1,2,...]
        group_ids = [x[0] for x in result.all()]
        return group_ids

    @ classmethod
    def count_by_id(cls, id) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.id == id, cls.delete_time == None)
        count = result.scalar()
        return count
