from lin import BaseCrud
from sqlalchemy import Column, Integer, String


class Qiniu(BaseCrud):
    __tablename__ = "qiniu"

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
