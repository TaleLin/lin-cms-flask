"""
    a standard CRUD template of book
    通过 图书 来实现一套标准的 CRUD 功能，供学习
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask.globals import current_app
from lin import permission_meta
from lin.exception import NotFound, ParameterError, Success
from lin.interface import LinViewModel
from lin.jwt import group_required, login_required
from lin.redprint import Redprint
from app.model.v1.book import Book
from app.validator.form import BookSearchForm, CreateOrUpdateBookForm
from app.validator.spectree import BookSchema, Query, BookResp,Data,Language,Cookie,Header, Response
from app.api import openapi
from flask import request
from app.validator.spectree import BaseModel

book_api = Redprint("book")

class BookViewModel(LinViewModel):
    """
    继承LinModel类可以自动序列化
    """
    def __init__(self, book):
        self.title = book.title
        self.author = book.author
        self.summary = book.summary


@book_api.route("/<bid>/base", methods=["GET"])
def get_book_base(bid):
    book = Book.get_detail(bid)
    return BookViewModel(book)


@book_api.route("/<bid>", methods=["GET"])
@login_required
def get_book(bid):
    book = Book.get_detail(bid)
    return book


@book_api.route("", methods=["GET"])
# @login_required
def get_books():
    books = Book.get_all()
    return books


@book_api.route("/search", methods=["GET"])
def search():
    form = BookSearchForm().validate_for_api()
    books = Book.search_by_keywords(form.q.data)
    return books
    



class SubRes(BaseModel):
    message:str = "哈哈"
    tt:int = 17


lbook = Book()
lbook.author = "aa"
lbook.title ="bb"
lbook.summary = "cc"
bv = BookViewModel(lbook)

class OuterRes(BaseModel):
    http_status_code:int = 201
    name:str= "haha"
    age:int = 18
    test:SubRes
    t:str = ParameterError("hello").message
    # tttt:bv



@book_api.route("", methods=["POST"])
@openapi.validate(json=BookSchema, resp=Response(ParameterError("你好，出错了"), NotFound, http_323={"a":1},http_333=OuterRes, http_213=bv), tags=["book"],)
def create_book():
    '''
    create the book
    '''
    # form = CreateOrUpdateBookForm().validate_for_api()
    # Book.new_book(request.context.json)
    json=request.context.json
    Book.create(
        title=json.title,
        author=json.author,
        summary=json.summary,
        image=json.image,
        commit=True,
    )
    return Success(12)


@book_api.route("/<bid>", methods=["PUT"])
def update_book(bid):
    form = CreateOrUpdateBookForm().validate_for_api()
    Book.edit_book(bid, form)
    return Success(13)


@book_api.route("/<bid>", methods=["DELETE"])
# @permission_meta(auth="删除图书", module="图书")
# @group_required
def delete_book(bid):
    Book.remove_book(bid)
    return Success(14)
