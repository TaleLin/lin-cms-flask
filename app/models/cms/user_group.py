from app.lin.interface import BaseCrud
from app.lin.db import db


class UserGroup(BaseCrud):
    __tablename__ = 'lin_user_group'
    __table_args__ = (Index('user_id_group_id', 'user_id', 'group_id'), )

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, comment='用户id')
    group_id = Column(Integer(), nullable=False, comment='分组id')

    @staticmethod
    def insert_batch(user_group_list, commit=False):
        db.session.add_all(user_group_list)
        if commit:
            db.session.commit()
