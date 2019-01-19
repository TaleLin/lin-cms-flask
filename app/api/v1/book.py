"""
    a standard CRUD template of book
    通过 图书 来实现一套标准的 CRUD 功能，供学习
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from lin import db, route_meta, group_required
from lin.redprint import Redprint
from flask import jsonify
from lin.exception import NotFound, ParameterException, Success

from app.libs.error_code import BookNotFound
from app.models.book import Book
from app.validators.forms import BookSearchForm, CreateOrUpdateBookForm

book_api = Redprint('book')


@book_api.route('/<id>', methods=['GET'])
def get_book(id):
    book = Book.query.filter_by(id=id).first()  # 通过Book模型在数据库中查询id=`id`的书籍
    if book is None:
        raise NotFound(msg='没有找到相关书籍')  # 如果书籍不存在，返回一个异常给前端
    return jsonify(book)  # 如果存在，返回该数据的信息


@book_api.route('/', methods=['GET'])
def get_books():
    books = Book.query.filter_by(delete_time=None).all()
    if books is None or len(books) < 1:
        raise NotFound(msg='没有找到相关书籍')
    return jsonify(books)


@book_api.route('/search', methods=['GET'])
def search():
    form = BookSearchForm().validate_for_api()
    q = '%' + form.q.data + '%'
    books = Book.query.filter(Book.title.like(q)).all()
    if books is None or len(books) < 1:
        raise BookNotFound()
    return jsonify(books)


@book_api.route('/', methods=['POST'])
def create_book():
    form = CreateOrUpdateBookForm().validate_for_api()  # 校验参数
    book = Book.query.filter_by(title=form.title.data).filter(Book.delete_time == None).first()  # 避免同名图书
    if book is not None:
        raise ParameterException(msg='图书已存在')
    # 新增图书
    with db.auto_commit():
        new_book = Book()
        new_book.title = form.title.data
        new_book.author = form.author.data
        new_book.summary = form.summary.data
        new_book.image = form.image.data
        db.session.add(new_book)
    return Success(msg='新建图书成功')


@book_api.route('/<id>', methods=['PUT'])
def update_book(id):
    form = CreateOrUpdateBookForm().validate_for_api()  # 校验参数
    book = Book.query.filter_by(id=id).first()  # 通过Book模型在数据库中查询id=`id`的书籍
    if book is None:
        raise NotFound(msg='没有找到相关书籍')  # 如果书籍不存在，返回一个异常给前端
    # 更新图书
    with db.auto_commit():
        book.title = form.title.data
        book.author = form.author.data
        book.summary = form.summary.data
        book.image = form.image.data
    return Success(msg='更新图书成功')


@book_api.route('/<id>', methods=['DELETE'])
@route_meta(auth='删除图书', module='图书')
@group_required
def delete_book(id):
    book = Book.query.filter_by(id=id).first()  # 通过Book模型在数据库中查询id=`id`的书籍
    if book is None:
        raise NotFound(msg='没有找到相关书籍')  # 如果书籍不存在，返回一个异常给前端
    # 删除图书，软删除
    book.delete(commit=True)
    return Success(msg='删除图书成功')
