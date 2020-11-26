import os

from flask import current_app
from sqlalchemy import Column, Index, Integer, SmallInteger, String, func, text

from app.lin import db, manager
from app.lin.interface import BaseCrud, InfoCrud


class UserIdentity(InfoCrud):
    __tablename__ = 'lin_user_identity'

    id = Column(Integer(), primary_key=True)
    user_id = Column(Integer(), nullable=False, comment='用户id')
    identity_type = Column(String(100), nullable=False)
    identifier = Column(String(100))
    credential = Column(String(100))
