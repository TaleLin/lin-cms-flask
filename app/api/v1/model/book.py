"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from lin import InfoCrud as Base
from sqlalchemy import Column, Integer, String


class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default="未名")
    summary = Column(String(1000))
    image = Column(String(100))
