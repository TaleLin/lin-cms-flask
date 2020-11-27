import os

from flask import current_app
from sqlalchemy import Column, Index, Integer, SmallInteger, String, func, text

from app.lin import db, manager
from app.lin.interface import BaseCrud, InfoCrud


class UserGroup(BaseCrud):
    __tablename__ = "lin_user_group"
    __table_args__ = (Index("user_id_group_id", "user_id", "group_id"),)

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, comment="用户id")
    group_id = Column(Integer(), nullable=False, comment="分组id")

    @staticmethod
    def insert_batch(user_group_list, commit=False):
        db.session.add_all(user_group_list)
        if commit:
            db.session.commit()

    @classmethod
    def delete_batch_by_user_id_and_group_ids(
        cls, user_id, group_ids: list, commit=False
    ):
        cls.query.filter_by(user_id=user_id).filter(cls.group_id.in_(group_ids)).delete(
            synchronize_session=False
        )
        if commit:
            db.session.commit()
