from app.lin.interface import InfoCrud
from app.lin.db import db
from sqlalchemy import func
from sqlalchemy import Column, Integer, String


class Log(InfoCrud):
    __tablename__ = 'lin_log'

    id = Column(Integer(), primary_key=True)
    message = Column(String(450), comment='日志信息')
    user_id = Column(Integer(), nullable=False, comment='用户id')
    username = Column(String(24), comment='用户当时的昵称')
    status_code = Column(Integer(), comment='请求的http返回码')
    method = Column(String(20), comment='请求方法')
    path = Column(String(50), comment='请求路径')
    permission = Column(String(100), comment='访问哪个权限')

    @property
    def time(self):
        return int(round(self.create_time.timestamp() * 1000))

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

    @staticmethod
    def create_log(**kwargs):
        log = Log()
        for key in kwargs.keys():
            if hasattr(log, key):
                setattr(log, key, kwargs[key])
        db.session.add(log)
        if kwargs.get('commit') is True:
            db.session.commit()
        return log
