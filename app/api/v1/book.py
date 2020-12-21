"""
    a standard CRUD template of book
    通过 图书 来实现一套标准的 CRUD 功能，供学习
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import g, request
from lin import DocResponse, permission_meta
from lin.exception import Success
from lin.jwt import group_required, login_required
from lin.redprint import Redprint

from app.api import api
from app.exception.api import BookNotFound
from app.model.v1.book import Book
from app.validator.schema import (
    AuthorizationSchema,
    BookSchemaList,
    BookQuerySearchSchema,
    BookInSchema,
    BookOutSchema,
)

book_api = Redprint("book")


@book_api.route("/<int:id>", methods=["GET"])
@api.validate(
    resp=DocResponse(BookNotFound, r=BookOutSchema),
    tags=["图书"],
)
def get_book(id: int):
    """
    获取id指定图书的信息
    """
    book = Book.get(id=id)
    if book:
        return BookOutSchema.parse_obj(book)
    raise BookNotFound


@book_api.route("", methods=["GET"])
@api.validate(
    resp=DocResponse(r=BookSchemaList),
    tags=["图书"],
)
def get_books():
    """
    获取图书列表
    """
    books = Book.get(one=False)
    return BookSchemaList.parse_obj(books)


@book_api.route("/search", methods=["GET"])
@api.validate(
    query=BookQuerySearchSchema,
    resp=DocResponse(BookNotFound, r=BookSchemaList),
    tags=["图书"],
)
def search():
    """
    关键字搜索图书
    """
    books = Book.query.filter(
        Book.title.like("%" + g.q + "%"), Book.delete_time == None
    ).all()
    if books:
        return BookSchemaList.parse_obj(books)
    raise BookNotFound


@book_api.route("", methods=["POST"])
@login_required
@api.validate(
    headers=AuthorizationSchema,
    json=BookInSchema,
    resp=DocResponse(Success(12)),
    tags=["图书"],
)
def create_book():
    """
    创建图书
    """
    book_schema = request.context.json
    Book.create(**book_schema.dict(), commit=True)
    return Success(12)


@book_api.route("/<int:id>", methods=["PUT"])
@login_required
@api.validate(
    headers=AuthorizationSchema,
    json=BookInSchema,
    resp=DocResponse(Success(13)),
    tags=["图书"],
)
def update_book(id: int):
    """
    更新图书信息
    """
    book_schema = request.context.json
    book = Book.get(id=id)
    if book:
        book.update(
            id=id,
            **book_schema.dict(),
            commit=True,
        )
        return Success(13)
    raise BookNotFound


@book_api.route("/<int:id>", methods=["DELETE"])
@permission_meta(name="删除图书", module="图书")
@group_required
@api.validate(
    headers=AuthorizationSchema,
    resp=DocResponse(BookNotFound, Success(14)),
    tags=["图书"],
)
def delete_book(id: int):
    """
    传入id删除对应图书
    """
    book = Book.get(id=id)
    if book:
        # 删除图书，软删除
        book.delete(commit=True)
        return Success(14)
    raise BookNotFound
