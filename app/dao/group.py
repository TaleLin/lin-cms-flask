"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from itertools import groupby
from operator import itemgetter

from lin.core import Group, manager
from lin.db import get_total_nums, db
from lin.exception import NotFound, Forbidden

from app.dao.auth import AuthDAO
from app.libs.utils import paginate


class GroupDAO(Group):
    def __init__(self):
        super(GroupDAO, self).__init__()

    def get_groups_info(self):
        start, count = paginate()
        groups = self.query.filter().offset(
            start).limit(count).all()
        if groups is None:
            raise NotFound(msg='不存在任何权限组')

        for group in groups:
            AuthDAO().get_by_group_id(group)

        total_nums = get_total_nums(manager.group_model)
        return groups, total_nums

    def get_single_info(self, gid):
        group = self.get(id=gid, one=True, soft=False)
        if group is None:
            raise NotFound(msg='分组不存在')
        AuthDAO().get_by_group_id(group)
        return group

    def get_all(self):
        groups = self.get(one=False)
        if groups is None:
            raise NotFound(msg='不存在任何权限组')
        return groups

    def new_group(self, form):
        exists = self.get(name=form.name.data)
        if exists:
            raise Forbidden(msg='分组已存在，不可创建同名分组')
        with db.auto_commit():
            group = self.create(name=form.name.data, info=form.info.data)
            db.session.flush()
            AuthDAO().create_auths(form.auths.data, group.id)

    def update_group(self, gid, form):
        exists = self.get(id=gid)
        if not exists:
            raise NotFound(msg='分组不存在，更新失败')
        exists.update(name=form.name.data, info=form.info.data, commit=True)

    def remove_group(self, gid):
        exist = self.get(id=gid)
        if not exist:
            raise NotFound(msg='分组不存在，删除失败')
        if manager.user_model.get(group_id=gid):
            raise Forbidden(msg='分组下存在用户，不可删除')
        # 删除group拥有的权限
        AuthDAO().delete_auths_by_gid(gid)
        exist.delete(commit=True)

    @staticmethod
    def split_modules(auths):
        auths.sort(key=itemgetter('module'))
        tmps = groupby(auths, itemgetter('module'))
        res = []
        for key, group in tmps:
            res.append({key: list(group)})
        return res
