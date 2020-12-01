"""
    a standard CRUD template of book
    通过 图书 来实现一套标准的 CRUD 功能，供学习
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from app.lin.interface import LinViewModel
from app.lin import permission_meta
from app.lin.exception import Success
from app.lin.jwt import group_required, login_required
from app.lin.redprint import Redprint
from app.model.v1.book import Book
from app.validator.form import BookSearchForm, CreateOrUpdateBookForm

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
@login_required
def get_books():
    books = Book.get_all()
    return books


@book_api.route("/search", methods=["GET"])
def search():
    form = BookSearchForm().validate_for_api()
    books = Book.search_by_keywords(form.q.data)
    return books


@book_api.route("", methods=["POST"])
def create_book():
    form = CreateOrUpdateBookForm().validate_for_api()
    Book.new_book(form)
    return Success(12)


@book_api.route("/<bid>", methods=["PUT"])
def update_book(bid):
    form = CreateOrUpdateBookForm().validate_for_api()
    Book.edit_book(bid, form)
    return Success(13)


@book_api.route("/<bid>", methods=["DELETE"])
@permission_meta(auth="删除图书", module="图书")
@group_required
def delete_book(bid):
    Book.remove_book(bid)
    return Success(14)
