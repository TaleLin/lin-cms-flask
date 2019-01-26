from lin.core import lin_config
from lin.exception import NotFound
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer, Text


class Poem(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False, comment='标题')
    author = Column(String(50), default='未名', comment='作者')
    dynasty = Column(String(50), default='未知', comment='朝代')
    content = Column(Text, nullable=False, comment='内容')
    image = Column(String(255), default='', comment='配图')

    def get_all(self):
        poems = self.query.filter_by(delete_time=None).limit(
            lin_config.get_config('poem.limit')
        ).all()
        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems

    def search(self, q):
        poems = self.query.filter(Poem.title.like('%' + q + '%')).all()
        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems
