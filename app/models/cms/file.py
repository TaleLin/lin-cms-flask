from app.lin.interface import InfoCrud
from app.lin.db import db
from sqlalchemy import func


class File(InfoCrud):
    __tablename__ = 'lin_file'
    __table_args__ = (Index('md5_del', 'md5', 'delete_time', unique=True), )

    id = Column(Integer(), primary_key=True)
    path = Column(String(500), nullable=False)
    type = Column(String(10), nullable=False, server_default=text(
        "'LOCAL'"), comment='LOCAL 本地，REMOTE 远程')
    name = Column(String(100), nullable=False)
    extension = Column(String(50))
    size = Column(Integer())
    md5 = Column(String(40), comment='md5值，防止上传重复文件')

    @classmethod
    def select_by_md5(cls, md5):
        result = cls.query.filter_by(soft=True, md5=md5)
        file = result.first()
        return file

    @classmethod
    def count_by_md5(cls, md5):
        result = db.session.query(func.count(cls.id)).filter(
            cls.delete_time == None, cls.md5 == md5)
        count = result.scalar()
        return count
