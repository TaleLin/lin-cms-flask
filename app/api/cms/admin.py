"""
    admin apis
    ~~~~~~~~~
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import math

from flask import Blueprint, g
from lin import (
    DocResponse,
    Forbidden,
    GroupLevelEnum,
    Logger,
    NotFound,
    ParameterError,
    Success,
    admin_required,
    db,
    manager,
    permission_meta,
)
from sqlalchemy import func

from app.api import AuthorizationBearerSecurity, api
from app.api.cms.schema import ResetPasswordSchema
from app.api.cms.schema.admin import (
    AdminGroupListSchema,
    AdminGroupPermissionSchema,
    AdminUserPageSchema,
    CreateGroupSchema,
    GroupBaseSchema,
    GroupIdWithPermissionIdListSchema,
    GroupQuerySearchSchema,
    UpdateUserInfoSchema,
)
from app.util.page import get_page_from_query

admin_api = Blueprint("admin", __name__)


@admin_api.route("/permission")
@permission_meta(name="查询所有可分配的权限", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
)
def permissions():
    """
    查询所有可分配的权限
    """
    return manager.get_ep_infos()


@admin_api.route("/users")
@permission_meta(name="查询所有用户", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(r=AdminUserPageSchema),
    before=GroupQuerySearchSchema.offset_handler,
)
def get_admin_users(query: GroupQuerySearchSchema):
    """
    查询所有用户
    """
    # 根据筛选条件和分页，获取 用户id 与 用户组id 的一对多 数据
    # 过滤root 分组
    query_root_group_id = db.session.query(manager.group_model.id).filter(
        manager.group_model.level == GroupLevelEnum.ROOT.value
    )
    _user_groups_list = db.session.query(
        manager.user_group_model.user_id.label("user_id"),
        func.group_concat(manager.user_group_model.group_id).label("group_ids"),
    ).filter(~manager.user_group_model.group_id.in_(query_root_group_id))
    if g.group_id:
        _user_groups_list = _user_groups_list.filter(
            manager.user_group_model.group_id == g.group_id
        )
    user_groups_list = (
        _user_groups_list.group_by(manager.user_group_model.user_id)
        .offset(g.offset)
        .limit(g.count)
        .all()
    )

    # 获取 符合条件的 用户id 数量
    # 过滤root 分组
    _total = db.session.query(
        func.count(func.distinct(manager.user_group_model.user_id))
    ).filter(~manager.user_group_model.group_id.in_(query_root_group_id))
    if g.group_id:
        _total = _total.filter(manager.user_group_model.group_id == g.group_id)
    total = _total.scalar()

    # 获取本次需要返回的用户的数据
    user_ids = [x.user_id for x in user_groups_list]
    users = manager.user_model.query.filter(manager.user_model.id.in_(user_ids)).all()
    user_dict = dict()
    for user in users:
        user.groups = list()
        user._fields.append("groups")
        user_dict[user.id] = user

    # 使用用户组来过滤，则不需要补全用户组信息
    if not g.group_id:
        # 拿到本次请求返回用户的所有 用户组 id List
        group_ids = [
            int(i)
            for i in set().union(*(x.group_ids.split(",") for x in user_groups_list))
        ]
        # 获取本次需要返回的用户组的数据
        groups = manager.group_model.query.filter(
            manager.group_model.id.in_(group_ids)
        ).all()
        group_dict = dict()
        for group in groups:
            group_dict[group.id] = group
        items = []

        # 根据 用户与用户组 一对多的关系， 补全用户的用户组详细信息
        for user_id, group_ids in user_groups_list:
            group_id_list = [int(gid) for gid in group_ids.split(",")]
            groups = [group_dict[group_id] for group_id in group_id_list]
            user_dict[user_id].groups = groups
            items.append(user_dict[user_id])

    total_page = math.ceil(total / g.count)
    page = get_page_from_query()
    return AdminUserPageSchema(
        count=g.count, total=total, total_page=total_page, page=page, items=users
    )


@admin_api.route("/user/<int:uid>/password", methods=["PUT"])
@permission_meta(name="修改用户密码", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    resp=DocResponse(NotFound("用户不存在"), Success("密码修改成功")),
    security=[AuthorizationBearerSecurity],
)
def change_user_password(uid: int, json: ResetPasswordSchema):
    """
    修改用户密码
    """

    user = manager.find_user(id=uid)
    if not user:
        raise NotFound("用户不存在")

    with db.auto_commit():
        user.reset_password(g.new_password)

    return Success("密码修改成功")


@admin_api.route("/user/<int:uid>", methods=["DELETE"])
@permission_meta(name="删除用户", module="管理员", mount=False)
@Logger(template="管理员删除了一个用户")
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(NotFound("用户不存在"), Success("删除成功"), Forbidden("用户不能删除")),
)
def delete_user(uid):
    """
    删除用户
    """
    user = manager.user_model.get(id=uid)
    if user is None:
        raise NotFound("用户不存在")
    groups = manager.group_model.select_by_user_id(uid)
    # 超级管理员分组的用户仅有一个分组
    if groups[0].level == GroupLevelEnum.ROOT.value:
        raise Forbidden("无法删除此用户")
    with db.auto_commit():
        manager.user_group_model.query.filter_by(user_id=uid).delete(
            synchronize_session=False
        )
        user.hard_delete()
    return Success("操作成功")


@admin_api.route("/user/<int:uid>", methods=["PUT"])
@permission_meta(name="管理员更新用户信息", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(
        NotFound("用户不存在"),
        Success("更新成功"),
        ParameterError("邮箱已被注册，请重新输入邮箱"),
    ),
)
def update_user(uid: int, json: UpdateUserInfoSchema):
    """
    更新用户信息
    """
    user = manager.user_model.get(id=uid)
    if user is None:
        raise NotFound("用户不存在")
    if user.email != g.email:
        exists = manager.user_model.get(email=g.email)
        if exists:
            raise ParameterError("邮箱已被注册，请重新输入邮箱")
    with db.auto_commit():
        user.email = g.email
        group_ids = g.group_ids
        # 清空原来的所有关联关系
        manager.user_group_model.query.filter_by(user_id=user.id).delete(
            synchronize_session=False
        )
        # 根据传入分组ids 新增关联记录
        user_group_list = list()
        # 如果没传分组数据，则将其设定为 guest 分组
        if not group_ids:
            group_ids = [manager.group_model.get(level=GroupLevelEnum.GUEST.value).id]
        for group_id in group_ids:
            user_group = manager.user_group_model()
            user_group.user_id = user.id
            user_group.group_id = group_id
            user_group_list.append(user_group)
        db.session.add_all(user_group_list)
    return Success("操作成功")


@admin_api.route("/group/all")
@permission_meta(name="查询所有分组", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(NotFound("不存在任何分组"), r=AdminGroupListSchema),
)
def get_all_group():
    """
    获取所有分组
    """
    groups = manager.group_model.query.filter(
        manager.group_model.is_deleted == False,
        manager.group_model.level != GroupLevelEnum.ROOT.value,
    ).all()
    if groups is None:
        raise NotFound("不存在任何分组")
    return groups


@admin_api.route("/group/<int:gid>")
@permission_meta(name="查询一个分组及其权限", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(NotFound("分组不存在"), r=AdminGroupPermissionSchema),
)
def get_group(gid):
    """
    获取一个分组及其权限
    """
    group = manager.group_model.get(id=gid, one=True, soft=False)
    if group is None:
        raise NotFound("分组不存在")
    permissions = manager.permission_model.select_by_group_id(gid)
    setattr(group, "permissions", permissions)
    group._fields.append("permissions")
    return group


@admin_api.route("/group", methods=["POST"])
@permission_meta(name="新建分组", module="管理员", mount=False)
@Logger(template="管理员新建了一个分组")  # 记录日志
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(
        ParameterError("用户组已存在, 不可创建同名分组"),
        Success("新建用户组成功"),
    ),
)
def create_group(json: CreateGroupSchema):
    """
    新建分组
    """
    exists = manager.group_model.get(name=g.name)
    if exists:
        raise Forbidden("分组已存在，不可创建同名分组")
    with db.auto_commit():
        group = manager.group_model.create(
            name=g.name,
            info=g.info,
        )
        db.session.flush()
        group_permission_list = list()
        for permission_id in g.permission_ids:
            gp = manager.group_permission_model()
            gp.group_id = group.id
            gp.permission_id = permission_id
            group_permission_list.append(gp)
        db.session.add_all(group_permission_list)
    return Success("新建分组成功")


@admin_api.route("/group/<int:gid>", methods=["PUT"])
@permission_meta(name="更新一个分组", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(
        ParameterError("分组不存在,更新失败"),
        Success("更新分组成功"),
    ),
)
def update_group(gid, json: GroupBaseSchema):
    """
    更新一个分组基本信息
    """
    exists = manager.group_model.get(id=gid)
    if not exists:
        raise NotFound("分组不存在，更新失败")
    exists.update(name=g.name, info=g.info, commit=True)
    return Success("更新成功")


@admin_api.route("/group/<int:gid>", methods=["DELETE"])
@permission_meta(name="删除一个分组", module="管理员", mount=False)
@Logger(template="管理员删除一个分组")  # 记录日志
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(NotFound("分组不存在，删除失败"), Forbidden("分组不可删除"), Success("删除分组成功")),
)
def delete_group(gid):
    """
    删除一个分组
    """
    exist = manager.group_model.get(id=gid)
    if not exist:
        raise NotFound("分组不存在，删除失败")
    guest_group = manager.group_model.get(level=GroupLevelEnum.GUEST.value)
    root_group = manager.group_model.get(level=GroupLevelEnum.ROOT.value)
    if gid in (guest_group.id, root_group.id):
        raise Forbidden("不可删除此分组")
    if manager.user_model.select_page_by_group_id(gid, root_group.id):
        raise Forbidden("分组下存在用户，不可删除")
    with db.auto_commit():
        # 删除group id 对应的关联记录
        manager.group_permission_model.query.filter_by(group_id=gid).delete(
            synchronize_session=False
        )
        # 删除group
        exist.delete()
    return Success("删除分组成功")


@admin_api.route("/permission/dispatch/batch", methods=["POST"])
@permission_meta(name="分配多个权限", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    security=[AuthorizationBearerSecurity],
    resp=DocResponse(
        Success("添加权限成功"),
    ),
)
def dispatch_auths(json: GroupIdWithPermissionIdListSchema):
    """
    分配多个权限
    """
    with db.auto_commit():
        for permission_id in g.permission_ids:
            one = manager.group_permission_model.get(
                group_id=g.group_id, permission_id=permission_id
            )
            if not one:
                manager.group_permission_model.create(
                    group_id=g.group_id,
                    permission_id=permission_id,
                )
    return Success("添加权限成功")


@admin_api.route("/permission/remove", methods=["POST"])
@permission_meta(name="删除多个权限", module="管理员", mount=False)
@admin_required
@api.validate(
    tags=["管理员"],
    resp=DocResponse(Success("删除权限成功")),
    security=[AuthorizationBearerSecurity],
)
def remove_auths(json: GroupIdWithPermissionIdListSchema):
    """
    删除多个权限
    """

    with db.auto_commit():
        db.session.query(manager.group_permission_model).filter(
            manager.group_permission_model.permission_id.in_(g.permission_ids),
            manager.group_permission_model.group_id == g.group_id,
        ).delete(synchronize_session=False)

    return Success("删除权限成功")
