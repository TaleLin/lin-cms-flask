"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from lin.exception import NotFound, ParameterException
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer

from app.libs.error_code import BookNotFound


class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default='未名')
    summary = Column(String(1000))
    image = Column(String(50))

    @classmethod
    def get_detail(cls, bid):
        book = cls.query.filter_by(id=bid, delete_time=None).first()
        if book is None:
            raise NotFound(msg='没有找到相关书籍')
        return book

    @classmethod
    def get_all(cls):
        books = cls.query.filter_by(delete_time=None).all()
        if not books:
            raise NotFound(msg='没有找到相关书籍')
        return books

    @classmethod
    def search_by_keywords(cls, q):
        books = cls.query.filter(Book.title.like('%' + q + '%'), Book.delete_time == None).all()
        if not books:
            raise BookNotFound()
        return books

    @classmethod
    def new_book(cls, form):
        book = Book.query.filter_by(title=form.title.data, delete_time=None).first()
        if book is not None:
            raise ParameterException(msg='图书已存在')

        Book.create(
            title=form.title.data,
            author=form.author.data,
            summary=form.summary.data,
            image=form.image.data,
            commit=True
        )
        return True

    @classmethod
    def edit_book(cls, bid, form):
        book = Book.query.filter_by(id=bid, delete_time=None).first()
        if book is None:
            raise NotFound(msg='没有找到相关书籍')

        book.update(
            id=bid,
            title=form.title.data,
            author=form.author.data,
            summary=form.summary.data,
            image=form.image.data,
            commit=True
        )
        return True

    @classmethod
    def remove_book(cls, bid):
        book = cls.query.filter_by(id=bid, delete_time=None).first()
        if book is None:
            raise NotFound(msg='没有找到相关书籍')
        # 删除图书，软删除
        book.delete(commit=True)
        return True
