from lin import Permission as LinPermission
from lin import db, manager


class Permission(LinPermission):
    @classmethod
    def select_by_group_id(cls, group_id) -> list:
        """
        传入用户组Id ，根据 Group-Permission关联表 获取 权限列表
        """
        query = db.session.query(manager.group_permission_model.permission_id).filter(
            manager.group_permission_model.group_id == group_id
        )
        result = cls.query.filter_by(soft=True, mount=True).filter(cls.id.in_(query))
        permissions = result.all()
        return permissions

    @classmethod
    def select_by_group_ids(cls, group_ids: list) -> list:
        """
        传入用户组Id列表 ，根据 Group-Permission关联表 获取 权限列表
        """
        query = db.session.query(manager.group_permission_model.permission_id).filter(
            manager.group_permission_model.group_id.in_(group_ids)
        )
        result = cls.query.filter_by(soft=True, mount=True).filter(cls.id.in_(query))
        permissions = result.all()
        return permissions

    @classmethod
    def select_by_group_ids_and_module(cls, group_ids: list, module) -> list:
        """
        传入用户组的 id 列表 和 权限模块名称，根据 Group-Permission关联表 获取 权限列表
        """
        query = db.session.query(manager.group_permission_model.permission_id).filter(
            manager.group_permission_model.group_id.in_(group_ids)
        )
        result = cls.query.filter_by(soft=True, module=module, mount=True).filter(cls.id.in_(query))
        permissions = result.all()
        return permissions
