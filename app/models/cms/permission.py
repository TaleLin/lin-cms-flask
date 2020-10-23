from app.lin.interface import InfoCrud
from app.lin.db import db


class Permission(InfoCrud):
    __tablename__ = 'lin_permission'

    id = Column(Integer(), primary_key=True)
    name = Column(String(60), nullable=False, comment='权限名称，例如：访问首页')
    module = Column(String(50), nullable=False, comment='权限所属模块，例如：人员管理')
    mount = Column(SmallInteger(), nullable=False,
                   server_default=text("1"), comment='0：关闭 1：开启')

    @classmethod
    def select_by_group_id(cls, group_id) -> list:
        from .group_permission import GroupPermission
        ''' 
        传入用户组Id ，根据 Group-Permission关联表 获取 权限列表
        '''
        query = db.session.query(GroupPermission.permission_id).filter(
            GroupPermission.group_id == group_id)
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        permissions = result.all()
        return permissions

    @classmethod
    def select_by_group_ids(cls, group_ids: list) -> list:
        ''' 
        传入用户组Id列表 ，根据 Group-Permission关联表 获取 权限列表
        '''
        from .group_permission import GroupPermission
        query = db.session.query(GroupPermission.permission_id).filter(
            GroupPermission.group_id.in_(group_ids))
        result = cls.query.filter_by(soft=True).filter(cls.id.in_(query))
        permissions = result.all()
        return permissions

    @classmethod
    def select_by_group_ids_and_module(cls, group_ids: list, module) -> list:
        '''
        传入用户组的 id 列表 和 权限模块名称，根据 Group-Permission关联表 获取 权限列表
        '''
        from .group_permission import GroupPermission
        query = db.session.query(GroupPermission.permission_id).filter(
            GroupPermission.group_id.in_(group_ids))
        result = cls.query.filter_by(
            soft=True, module=module).filter(cls.id.in_(query))
        permissions = result.all()
        return permissions
