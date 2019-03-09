from lin import db
from lin.core import lin_config
from lin.exception import NotFound
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer, Text, text


class Poem(Base):
    __tablename__ = 'lin_poem'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False, comment='标题')
    author = Column(String(50), default='未名', comment='作者')
    dynasty = Column(String(50), default='未知', comment='朝代')
    _content = Column('content', Text, nullable=False, comment='内容，以/来分割每一句，以|来分割宋词的上下片')
    image = Column(String(255), default='', comment='配图')

    @property
    def content(self):
        ret = []
        lis = self._content.split('|')
        for x in lis:
            ret.append(x.split('/'))
        return ret

    def get_all(self, form):
        query = self.query.filter_by(delete_time=None)

        if form.author.data:
            query = query.filter_by(author=form.author.data)

        limit = form.count.data if\
            form.count.data else lin_config.get_config('poem.limit')

        poems = query.limit(limit).all()

        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems

    def search(self, q):
        poems = self.query.filter(Poem.title.like('%' + q + '%')).all()
        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems

    @classmethod
    def get_authors(cls):
        authors = db.session.query(cls.author).filter_by(soft=False).group_by(
            text('author')).having(text('count(author) > 0')).all()
        ret = [author[0] for author in authors]
        return ret
