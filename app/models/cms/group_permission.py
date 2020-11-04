from app.lin.interface import BaseCrud
from app.lin.db import db
from sqlalchemy import (
    Column, DateTime, Index, Integer, SmallInteger, String, func, text)


class GroupPermission(BaseCrud):
    __tablename__ = 'lin_group_permission'
    __table_args__ = (Index('group_id_permission_id',
                            'group_id', 'permission_id'), )

    id = Column(Integer(), primary_key=True)
    group_id = Column(Integer(), nullable=False, comment='分组id')
    permission_id = Column(Integer(), nullable=False, comment='权限id')

    @staticmethod
    def insert_batch(group_permission_list, commit=False):
        db.session.add_all(group_permission_list)
        if commit:
            db.session.commit()

    @classmethod
    def delete_batch_by_group_id_and_permission_ids(cls, group_id, permission_ids: list, commit=False):
        cls.query.filter_by(group_id=group_id).filter(
            cls.permission_id.in_(permission_ids)).delete(synchronize_session=False)
        if commit:
            db.session.commit()
