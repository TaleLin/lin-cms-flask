"""
    a standard CRUD template of book
    通过 图书 来实现一套标准的 CRUD 功能，供学习
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import request
from lin import DocResponse, permission_meta
from lin.exception import DocParameterError, NotFound, Success
from lin.jwt import group_required, login_required
from lin.redprint import Redprint

from app.api import apidoc
from app.exception.api import BookNotFound
from app.model.v1.book import Book
from app.validator.schema import (
    AccessTokenSchema,
    BookListSchema,
    BookSchema,
    QuerySearchSchema,
)

book_api = Redprint("book")


@book_api.route("/<int:id>", methods=["GET"])
@apidoc.validate(
    resp=DocResponse(BookNotFound, http_200=BookSchema),
    tags=["图书"],
)
def get_book(id: int):
    """
    获取id指定图书的信息
    """
    book = Book.query.filter_by(id=id, delete_time=None).first()
    if not book:
        raise BookNotFound
    return BookSchema.parse_obj(book)


@book_api.route("", methods=["GET"])
@apidoc.validate(
    resp=DocResponse(http_200=BookListSchema),
    tags=["图书"],
)
def get_books():
    """
    获取图书列表
    """
    books = Book.query.filter_by(delete_time=None).all()
    # TODO JSON
    # return BookListSchema(items=books)
    return books


@book_api.route("/search", methods=["GET"])
@apidoc.validate(
    query=QuerySearchSchema,
    resp=DocResponse(BookNotFound, DocParameterError),
    tags=["图书"],
)
def search():
    """
    关键字搜索图书
    """
    keyword = request.context.query.q
    books = Book.query.filter(
        Book.title.like("%" + keyword + "%"), Book.delete_time == None
    ).all()
    if not books:
        raise BookNotFound
    # TODO JSON
    # return BookListSchema(items=books)
    return books


@book_api.route("", methods=["POST"])
@login_required
@apidoc.validate(
    headers=AccessTokenSchema,
    json=BookSchema,
    resp=DocResponse(DocParameterError, Success(12)),
    tags=["图书"],
)
def create_book():
    """
    创建图书
    """
    book_schema = request.context.json
    Book.create(
        **book_schema.dict(),
        commit=True,
    )
    return Success(12)


@book_api.route("/<int:id>", methods=["PUT"])
@login_required
@apidoc.validate(
    headers=AccessTokenSchema,
    json=BookSchema,
    resp=DocResponse(DocParameterError, Success(13)),
    tags=["图书"],
)
def update_book(id: int):
    """
    更新图书信息
    """
    book_schema = request.context.json
    book = Book.query.filter_by(id=id, delete_time=None).first()
    if book is None:
        raise BookNotFound
    book.update(
        id=id,
        commit=True,
        **book_schema.dict(),
    )
    return Success(13)


@book_api.route("/<int:id>", methods=["DELETE"])
@permission_meta(auth="删除图书", module="图书")
@group_required
@apidoc.validate(
    headers=AccessTokenSchema,
    resp=DocResponse(BookNotFound, Success(14)),
    tags=["图书"],
)
def delete_book(id: int):
    """
    传入id删除对应图书
    """
    book = Book.query.filter_by(id=id, delete_time=None).first()
    if book is None:
        raise BookNotFound
    # 删除图书，软删除
    book.delete(commit=True)
    return Success(14)
