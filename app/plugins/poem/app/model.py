from lin.exception import NotFound
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer


class Poem(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False, comment='标题')
    author = Column(String(50), default='未名', comment='作者')
    dynasty = Column(String(50), default='位置', comment='朝代')
    content = Column(String(255), nullable=False, comment='内容')

    def get_all(self):
        poems = self.query.filter_by(delete_time=None).all()
        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems

    def search(self, q):
        poems = self.query.filter(Poem.title.like('%' + q + '%')).all()
        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems
