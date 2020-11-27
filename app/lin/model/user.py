import os

from flask import current_app
from sqlalchemy import Column, Index, Integer, SmallInteger, String, func, text

from app.lin import db, manager
from app.lin.interface import BaseCrud, InfoCrud
from app.lin.enums import GroupLevel
from werkzeug.security import check_password_hash, generate_password_hash                                                                                              



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
        self._exclude = ['delete_time','password']

    @property
    def avatar(self):
        site_domain = current_app.config.get('SITE_DOMAIN') if current_app.config.get('SITE_DOMAIN') else "http://127.0.0.1:5000"
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
        result = db.session.query(func.count(cls.id)).filter(cls.email == email, cls.delete_time == None)
        count = result.scalar()
        return count
    @classmethod
    def count_by_id(cls, uid) -> int:
        result = db.session.query(func.count(cls.id)).filter(cls.id == uid, cls.delete_time == None)
        count = result.scalar()
        return count

    @classmethod
    def select_page_by_group_id(cls, group_id, root_group_id) -> list:
        ''' 通过分组id分页获取用户数据 '''
        query = db.session.query(manager.user_group_model.user_id).filter(manager.user_group_model.group_id == group_id, manager.user_group_model.group_id != root_group_id) 
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        users = result.all()
        return users

    @staticmethod
    def count_by_id_and_group_name(user_id, group_name) -> int:
        stmt = db.session.query(manager.group_model.id.label('group_id')).filter_by(soft=True, name=group_name).subquery()
        result = db.session.query(func.count(manager.user_group_model.id)).filter(manager.user_group_model.user_id == user_id, manager.user_group_model.group_id == stmt.c.group_id)
        count = result.scalar()
        return count

    @property
    def is_admin(self):
        return manager.user_group_model.get(user_id=self.id).group_id == GroupLevel.ROOT.value

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
            user_identity.identity_type ='USERNAME_PASSWORD'
            user_identity.identity ='root'
            user_identity.credential = generate_password_hash(raw)
            db.session.add(user_identity)

    def check_password(self, raw):                                                                                                                                     
        return check_password_hash(self.password, raw)

    def reset_password(self, new_password):
        self.password = new_password

    def change_password(self, old_password, new_password):
        if self.check_password(old_password):
            self.password = new_password
            return True
        return False

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

