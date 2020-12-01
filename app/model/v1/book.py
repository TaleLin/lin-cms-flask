"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy import Column, Integer, String

from app.common.exception import BookNotFound, BookParameterError
from lin.interface import InfoCrud as Base


class Book(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    author = Column(String(30), default="未名")
    summary = Column(String(1000))
    image = Column(String(50))

    @classmethod
    def get_detail(cls, bid):
        book = cls.query.filter_by(id=bid, delete_time=None).first()
        if book is None:
            raise BookNotFound()
        return book

    @classmethod
    def get_all(cls):
        books = cls.query.filter_by(delete_time=None).all()
        return books

    @classmethod
    def search_by_keywords(cls, q):
        books = cls.query.filter(
            Book.title.like("%" + q + "%"), Book.delete_time == None
        ).all()
        if not books:
            raise BookNotFound()
        return books

    @classmethod
    def new_book(cls, form):
        book = Book.query.filter_by(title=form.title.data, delete_time=None).first()
        if book is not None:
            raise BookParameterError("书籍已存在")

        Book.create(
            title=form.title.data,
            author=form.author.data,
            summary=form.summary.data,
            image=form.image.data,
            commit=True,
        )
        return True

    @classmethod
    def edit_book(cls, bid, form):
        book = Book.query.filter_by(id=bid, delete_time=None).first()
        if book is None:
            raise BookNotFound()

        book.update(
            id=bid,
            title=form.title.data,
            author=form.author.data,
            summary=form.summary.data,
            image=form.image.data,
            commit=True,
        )
        return True

    @classmethod
    def remove_book(cls, bid):
        book = cls.query.filter_by(id=bid, delete_time=None).first()
        if book is None:
            raise BookNotFound()
        # 删除图书，软删除
        book.delete(commit=True)
        return True
