"""
    db of Lin
    ~~~~~~~~~
    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery
from sqlalchemy import inspect, orm, func
from contextlib import contextmanager

from .exception import NotFound


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e


class Query(BaseQuery):

    def filter_by(self, soft=False, **kwargs):
        # soft 应用软删除
        if soft:
            kwargs['delete_time'] = None
        return super(Query, self).filter_by(**kwargs)

    def get_or_404(self, ident):
        rv = self.get(ident)
        if not rv:
            raise NotFound()
        return rv

    def first_or_404(self):
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv


db = SQLAlchemy(query_class=Query)


def get_total_nums(cls, is_soft=False, **kwargs):
    nums = db.session.query(func.count(cls.id))
    nums = nums.filter(cls.delete_time == None).filter_by(**kwargs).scalar() if is_soft else nums.filter().scalar()
    if nums:
        return nums
    else:
        return 0


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).columns
        if not self._fields:
            all_columns = set([column.name for column in columns])
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)
