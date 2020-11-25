from app.lin.interface import InfoCrud
from app.lin.db import db
from sqlalchemy import func
from sqlalchemy import (
    Column, DateTime, Index, Integer, SmallInteger, String, func, text)


class User(InfoCrud):
    __tablename__ = 'lin_user'
    __table_args__ = (Index('username_del',
                            'username',
                            'delete_time',
                            unique=True),
                      Index('email_del', 'email', 'delete_time', unique=True))

    id = Column(Integer(), primary_key=True)
    username = Column(String(24), nullable=False, comment='用户名，唯一')
    nickname = Column(String(24), comment='用户昵称')
    _avatar = Column('avatar', String(500), comment='头像url')
    email = Column(String(100), comment='邮箱')

    def _set_fields(self):
        self._exclude = ['delete_time']

    @property
    def avatar(self):
        site_domain = current_app.config.get(
            'SITE_DOMAIN') if current_app.config.get(
                'SITE_DOMAIN') else "http://127.0.0.1:5000"
        if self._avatar is not None:
            return site_domain + os.path.join(current_app.static_url_path, self._avatar)

    @classmethod
    def count_by_username(cls, username) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.username == username, cls.delete_time == None)
        count = result.scalar()
        return count

    @classmethod
    def count_by_email(cls, email) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.email == email, cls.delete_time == None)
        count = result.scalar()
        return count

    @classmethod
    def count_by_id(cls, uid) -> int:
        result = db.session.query(func.count(cls.id)).filter(
            cls.id == uid, cls.delete_time == None)
        count = result.scalar()
        return count

    @classmethod
    def select_page_by_group_id(cls, group_id, root_group_id) -> list:
        '''
        通过分组id分页获取用户数据, page 传哪呢
        '''
        from . import UserGroup
        query = db.session.query(UserGroup.user_id).filter(
            UserGroup.group_id == group_id,
            UserGroup.group_id != root_group_id)
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        users = result.all()
        return users

    @staticmethod
    def count_by_id_and_group_name(user_id, group_name) -> int:
        from . import UserGroup
        from . import Group
        stmt = db.session.query(Group.id.label('group_id')).filter_by(
            soft=True, name=group_name).subquery()
        result = db.session.query(func.count(UserGroup.id)).filter(
            UserGroup.user_id == user_id,
            UserGroup.group_id == stmt.c.group_id)
        count = result.scalar()
        return count
