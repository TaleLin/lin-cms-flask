"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from lin import db
from lin.core import Auth, manager, find_auth_module
from lin.exception import Forbidden


class AuthDAO(Auth):
    def __init__(self):
        super(AuthDAO, self).__init__()

    def get_by_group_id(self, group):
        auths = db.session.query(
            manager.auth_model.auth, manager.auth_model.module
        ).filter_by(soft=False, group_id=group.id).all()

        auths = [{'auth': auth[0], 'module': auth[1]} for auth in auths]
        from .group import GroupDAO
        res = GroupDAO.split_modules(auths)
        setattr(group, 'auths', res)
        group._fields.append('auths')

        return auths

    def create_auths(self, auths, group_id):
        for auth in auths:
            meta = find_auth_module(auth)
            if meta:
                self.create(auth=meta.auth, module=meta.module, group_id=group_id)

    def delete_auths_by_gid(self, group_id):
        self.query.filter(manager.auth_model.group_id == group_id).delete()

    def remove_auths(self, form):
        with db.auto_commit():
            self.query(manager.auth_model).filter(
                manager.auth_model.auth.in_(form.auths.data),
                manager.auth_model.group_id == form.group_id.data
            ).delete(synchronize_session=False)

    def patch_one(self, form):
        one = manager.auth_model.get(group_id=form.group_id.data, auth=form.auth.data)
        if one:
            raise Forbidden(msg='已有权限，不可重复添加')
        meta = find_auth_module(form.auth.data)
        self.create(
            group_id=form.group_id.data,
            auth=meta.auth,
            module=meta.module,
            commit=True
        )

    def patch_all(self, form):
        with db.auto_commit():
            for auth in form.auths.data:
                one = self.get(group_id=form.group_id.data, auth=auth)
                if not one:
                    meta = find_auth_module(auth)
                    self.create(
                        group_id=form.group_id.data,
                        auth=meta.auth,
                        module=meta.module
                    )
