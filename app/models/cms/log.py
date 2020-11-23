from app.lin.interface import InfoCrud
from app.lin.db import db
from sqlalchemy import func
from datetime import datetime


class Log(InfoCrud):
    __tablename__ = 'lin_log'

    id = Column(Integer(), primary_key=True)
    message = Column(String(450))
    user_id = Column(Integer(), nullable=False)
    username = Column(String(24))
    status_code = Column(Integer())
    method = Column(String(20))
    path = Column(String(50))
    permission = Column(String(100))

    @classmethod
    def select_by_conditions(cls, **kwargs) -> list:
        '''
        根据条件筛选日志，条件的可以是所有表内字段，以及start, end 时间段，keyword模糊匹配message字段
        '''
        conditions = dict()
        # 过滤 传入参数
        avaliable_keys = [
            c for c in vars(LogInterface).keys() if not c.startswith('_')
        ] + ['start', 'end', 'keyword']
        for key, value in kwargs.items():
            if key in avaliable_keys:
                conditions[key] = value
        query = cls.query.filter_by(soft=True)
        # 搜索特殊字段
        if conditions.get('start'):
            query = query.filter(cls.create_time > conditions.get('start'))
            del conditions['start']
        if conditions.get('end'):
            query = query.filter(cls.create_time < conditions.get('end'))
            del conditions['end']
        if conditions.get('keyword'):
            query = query.filter(
                cls.message.like(
                    '%{keyword}%'.format(keyword=conditions.get('keyword'))))
            del conditions['keyword']
        # 搜索表内字段
        query = query.filter_by(**conditions).group_by(
            cls.create_time).order_by(cls.create_time.desc())
        logs = query.all()
        return logs

    @classmethod
    def get_usernames(cls) -> list:
        result = db.session.query(
            cls.username).filter(cls.delete_time == None).group_by(
                cls.username).having(func.count(cls.username) > 0)
        # [(‘张三',),('李四',),...] -> ['张三','李四',...]
        usernames = [x[0] for x in result.all()]
        return usernames
