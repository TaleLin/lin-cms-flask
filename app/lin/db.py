"""
    db of Lin
    ~~~~~~~~~
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import os
from collections import OrderedDict
from contextlib import contextmanager
from inspect import isclass

import tablib
from flask import json
from flask_sqlalchemy import BaseQuery
from flask_sqlalchemy import Model as _Model
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc, func, inspect, orm, text
from sqlalchemy.pool import QueuePool

from .exception import NotFound


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


class Record(object):
    """A row, from a query, from a database."""

    __slots__ = ("_keys", "_values")

    def __init__(self, keys, values):
        self._keys = keys
        self._values = values

        # Ensure that lengths match properly.
        assert len(self._keys) == len(self._values)

    def keys(self):
        """Returns the list of column names from the query."""
        return self._keys

    def values(self):
        """Returns the list of values from the query."""
        return self._values

    def __repr__(self):
        return "<Record {}>".format(self.export("json")[1:-1])

    def __getitem__(self, key):
        # Support for index-based lookup.
        if isinstance(key, int):
            return self.values()[key]

        # Support for string-based lookup.
        if key in self.keys():
            i = self.keys().index(key)
            if self.keys().count(key) > 1:
                raise KeyError("Record contains multiple '{}' fields.".format(key))
            return self.values()[i]

        raise KeyError("Record contains no '{}' field.".format(key))

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError(e)

    def __dir__(self):
        standard = dir(super(Record, self))
        # Merge standard attrs with generated ones (from column names).
        return sorted(standard + [str(k) for k in self.keys()])

    def get(self, key, default=None):
        """Returns the value for a given key, or default."""
        try:
            return self[key]
        except KeyError:
            return default

    def as_dict(self, ordered=False):
        """Returns the row as a dictionary, as ordered."""
        items = zip(self.keys(), self.values())

        return OrderedDict(items) if ordered else dict(items)

    @property
    def dataset(self):
        """A Tablib Dataset containing the row."""
        data = tablib.Dataset()
        data.headers = self.keys()

        row = _reduce_datetimes(self.values())
        data.append(row)

        return data

    def export(self, format, **kwargs):
        """Exports the row to the given format."""
        return self.dataset.export(format, **kwargs)


class RecordCollection(object):
    """A set of excellent Records from a query."""

    def __init__(self, rows):
        self._rows = rows
        self._all_rows = []
        self.pending = True

    def __repr__(self):
        return "<RecordCollection size={} pending={}>".format(len(self), self.pending)

    def __iter__(self):
        """Iterate over all rows, consuming the underlying generator
        only when necessary."""
        i = 0
        while True:
            # Other code may have iterated between yields,
            # so always check the cache.
            if i < len(self):
                yield self[i]
            else:
                # Throws StopIteration when done.
                # Prevent StopIteration bubbling from generator, following https://www.python.org/dev/peps/pep-0479/
                try:
                    yield next(self)
                except StopIteration:
                    return
            i += 1

    def next(self):
        return self.__next__()

    def __next__(self):
        try:
            nextrow = next(self._rows)
            self._all_rows.append(nextrow)
            return nextrow
        except StopIteration:
            self.pending = False
            raise StopIteration("RecordCollection contains no more rows.")

    def __getitem__(self, key):
        is_int = isinstance(key, int)

        # Convert RecordCollection[1] into slice.
        if is_int:
            key = slice(key, key + 1)

        while len(self) < key.stop or key.stop is None:
            try:
                next(self)
            except StopIteration:
                break

        rows = self._all_rows[key]
        if is_int:
            return rows[0]
        else:
            return RecordCollection(iter(rows))

    def __len__(self):
        return len(self._all_rows)

    def export(self, format, **kwargs):
        """Export the RecordCollection to a given format (courtesy of Tablib)."""
        return self.dataset.export(format, **kwargs)

    @property
    def dataset(self):
        """A Tablib Dataset representation of the RecordCollection."""
        # Create a new Tablib Dataset.
        data = tablib.Dataset()

        # If the RecordCollection is empty, just return the empty set
        # Check number of rows by typecasting to list
        if len(list(self)) == 0:
            return data

        # Set the column names as headers on Tablib Dataset.
        first = self[0]

        data.headers = first.keys()
        for row in self.all():
            row = _reduce_datetimes(row.values())
            data.append(row)

        return data

    def all(self, as_dict=False, as_ordereddict=False):
        """Returns a list of all rows for the RecordCollection. If they haven't
        been fetched yet, consume the iterator and cache the results."""

        # By calling list it calls the __iter__ method
        rows = list(self)

        if as_dict:
            return [r.as_dict() for r in rows]
        elif as_ordereddict:
            return [r.as_dict(ordered=True) for r in rows]

        return rows

    def as_dict(self, ordered=False):
        return self.all(as_dict=not (ordered), as_ordereddict=ordered)

    def first(self, default=None, as_dict=False, as_ordereddict=False):
        """Returns a single record for the RecordCollection, or `default`. If
        `default` is an instance or subclass of Exception, then raise it
        instead of returning it."""

        # Try to get a record, or return/raise default.
        try:
            record = self[0]
        except IndexError:
            if isexception(default):
                raise default
            return default

        # Cast and return.
        if as_dict:
            return record.as_dict()
        elif as_ordereddict:
            return record.as_dict(ordered=True)
        else:
            return record

    def one(self, default=None, as_dict=False, as_ordereddict=False):
        """Returns a single record for the RecordCollection, ensuring that it
        is the only record, or returns `default`. If `default` is an instance
        or subclass of Exception, then raise it instead of returning it."""

        # Ensure that we don't have more than one row.
        try:
            self[1]
        except IndexError:
            return self.first(
                default=default, as_dict=as_dict, as_ordereddict=as_ordereddict
            )
        else:
            raise ValueError(
                "RecordCollection contained more than one row. "
                "Expects only one row when using "
                "RecordCollection.one"
            )

    def scalar(self, default=None):
        """Returns the first column of the first row, or `default`."""
        row = self.one()
        return row[0] if row else default


class Connection(object):
    """A Database connection."""

    def __init__(self, connection):
        self._conn = connection

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def __repr__(self):
        return "<Connection open={}>".format(not self._conn.closed)

    def query(self, query, fetchall=False, **params):
        """Executes the given SQL query against the connected Database.
        Parameters can, optionally, be provided. Returns a RecordCollection,
        which can be iterated over to get result rows as dictionaries.
        """

        # Execute the given query.
        cursor = self._conn.execute(text(query), **params)  # TODO: PARAMS GO HERE

        # Row-by-row Record generator.
        row_gen = (Record(cursor.keys(), row) for row in cursor)

        # Convert psycopg2 results to RecordCollection.
        results = RecordCollection(row_gen)

        # Fetch all results if desired.
        if fetchall:
            results.all()

        return results

    def bulk_query(self, query, *multiparams):
        """Bulk insert or update."""

        self._conn.execute(text(query), *multiparams)

    def query_file(self, path, fetchall=False, **params):
        """Like Connection.query, but takes a filename to load a query from."""

        # If path doesn't exists
        if not os.path.exists(path):
            raise IOError("File '{}' not found!".format(path))

        # If it's a directory
        if os.path.isdir(path):
            raise IOError("'{}' is a directory!".format(path))

        # Read the given .sql file into memory.
        with open(path) as f:
            query = f.read()

        # Defer processing to self.query method.
        return self.query(query=query, fetchall=fetchall, **params)

    def bulk_query_file(self, path, *multiparams):
        """Like Connection.bulk_query, but takes a filename to load a query
        from.
        """

        # If path doesn't exists
        if not os.path.exists(path):
            raise IOError("File '{}'' not found!".format(path))

        # If it's a directory
        if os.path.isdir(path):
            raise IOError("'{}' is a directory!".format(path))

        # Read the given .sql file into memory.
        with open(path) as f:
            query = f.read()

        self._conn.execute(text(query), *multiparams)

    def transaction(self):
        """Returns a transaction object. Call ``commit`` or ``rollback``
        on the returned object as appropriate."""

        return self._conn.begin()


class RecordsException(Exception):
    """A records-specific exception."""

    pass


class Database(SQLAlchemy):
    def __init__(self, **kwargs):
        self.open = True
        super(Database, self).__init__(**kwargs)

    @property
    def dialect(self):
        return self.engine.dialect.name

    @property
    def checkedout(self):
        pool = self.engine.pool
        if isinstance(pool, QueuePool):
            return pool.checkedout()
        return 0

    def close(self, force=False):
        """Closes the Database.
        By default, the database must have no checked-out connections for this
        operation to complete. This may be overriden by setting force=True, but
        may result in stray connections.
        """
        if not force:
            pool = self.engine.pool
            if isinstance(pool, QueuePool) and pool.checkedout() != 0:
                err_msg = (
                    "Database has {} checked out connections. Consume "
                    "all RecordCollections created by this database "
                    "and try again.".format(pool.checkedout())
                )
                raise RecordsException(err_msg)

        self.engine.dispose()
        self.open = False

    def __enter__(self):
        return self

    def __exit__(self, exc, val, traceback):
        self.close()

    def get_table_names(self, internal=False):
        """Returns a list of table names for the connected database."""

        # Setup SQLAlchemy for Database inspection.
        return inspect(self.engine).get_table_names()

    def get_connection(self):
        """Get a connection to this Database. Connections are retrieved from a
        pool. The retrieved connection remains open until its result is
        consumed.
        """
        if not self.open:
            raise exc.ResourceClosedError("Database closed.")

        return Connection(self.engine.connect())

    def query(self, query, fetchall=False, **params):
        """Executes the given SQL query against the Database. Parameters can,
        optionally, be provided. Returns a RecordCollection, which can be
        iterated over to get result rows as dictionaries.
        """
        conn = self.get_connection()
        return conn.query(query, fetchall, **params)

    def bulk_query(self, query, *multiparams):
        """Bulk insert or update."""

        conn = self.get_connection()
        conn.bulk_query(query, *multiparams)

    def query_file(self, path, fetchall=False, **params):
        """Like Database.query, but takes a filename to load a query from."""

        conn = self.get_connection()
        return conn.query_file(path, fetchall, **params)

    def bulk_query_file(self, path, *multiparams):
        """Like Database.bulk_query, but takes a filename to load a query from."""

        conn = self.get_connection()
        conn.bulk_query_file(path, *multiparams)

    @contextmanager
    def transaction(self):
        """A context manager for executing a transaction on this Database."""

        conn = self.get_connection()
        tx = conn.transaction()
        try:
            yield conn
            tx.commit()
        except Exception as e:
            tx.rollback()
            raise e
        finally:
            conn.close()

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
            kwargs["delete_time"] = None
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


class Model(_Model):
    def __repr__(self):
        detail = json.dumps(
            {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        )
        identity = inspect(self).identity
        if identity is None:
            pk = "\n(transient {0} {1})\n".format(id(self), detail)
        else:
            pk = ",".join(to_str(value) for value in identity)
        return "\n<{0} {1} {2}>\n".format(type(self).__name__, pk, detail)


def isexception(obj):
    """Given an object, return a boolean indicating whether it is an instance
    or subclass of :py:class:`Exception`.
    """
    if isinstance(obj, Exception):
        return True
    if isclass(obj) and issubclass(obj, Exception):
        return True
    return False


def _reduce_datetimes(row):
    """Receives a row, converts datetimes to strings."""

    row = list(row)

    for i in range(len(row)):
        if hasattr(row[i], "isoformat"):
            row[i] = row[i].isoformat()
    return tuple(row)


def get_total_nums(cls, is_soft=False, **kwargs):
    nums = db.session.query(func.count(cls.id))
    nums = (
        nums.filter(cls.delete_time == None).filter_by(**kwargs).scalar()
        if is_soft
        else nums.filter().scalar()
    )
    if nums:
        return nums
    else:
        return 0


def to_str(x, charset="utf8", errors="strict"):
    if x is None or isinstance(x, str):
        return x

    if isinstance(x, bytes):
        return x.decode(charset, errors)

    return str(x)


db = Database(query_class=Query, model_class=Model)
