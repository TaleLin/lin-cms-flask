from sqlalchemy import Column, FetchedValue, Integer, String

from app.lin.interface import BaseCrud


class Image(BaseCrud):
    __tablename__ = "image"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    _from = Column("from", Integer, nullable=False, server_default=FetchedValue())
