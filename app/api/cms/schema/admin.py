import re
from typing import List, Optional

from lin import BaseModel, ParameterError
from pydantic import EmailStr, Field, validator

from app.schema import BasePageSchema, QueryPageSchema


class ResetPasswordSchema(BaseModel):
    new_password: str = Field(description="新密码", min_length=6, max_length=22)
    confirm_password: str = Field(description="确认密码", min_length=6, max_length=22)

    @validator("confirm_password", allow_reuse=True)
    def passwords_match(cls, v, values, **kwargs):
        if v != values["new_password"]:
            raise ParameterError("两次输入的密码不一致，请输入相同的密码")
        return v


class GroupIdListSchema(BaseModel):
    group_ids: List[int] = Field(description="用户组ID列表")

    @validator("group_ids", each_item=True)
    def check_group_id(cls, v, values, **kwargs):
        if v <= 0:
            raise ParameterError("用户组ID必须大于0")
        return v


class RegisterSchema(ResetPasswordSchema, GroupIdListSchema):
    username: str = Field(description="用户名", min_length=2, max_length=10)

    @validator("username")
    def check_username(cls, v, values, **kwargs):
        if not re.match(r"^[a-zA-Z0-9_]{2,10}$", v):
            raise ParameterError("用户名只能由字母、数字、下划线组成，且长度为2-10位")
        return v


class AdminGroupSchema(BaseModel):
    id: int = Field(description="用户组ID")
    info: str = Field(description="用户组信息")
    name: str = Field(description="用户组名称")


class AdminGroupListSchema(BaseModel):
    __root__: List[AdminGroupSchema]


class AdminUserSchema(BaseModel):
    id: int = Field(description="用户ID")
    username: str = Field(description="用户名")
    email: Optional[EmailStr] = Field(description="邮箱")
    groups: List[AdminGroupSchema] = Field(description="用户组列表")


class AdminUserPageSchema(BasePageSchema):
    items: List[AdminUserSchema]


class GroupQuerySearchSchema(QueryPageSchema):
    group_id: Optional[int] = Field(gt=0, description="用户组ID")


class UpdateUserInfoSchema(GroupIdListSchema):
    email: EmailStr = Field(description="电子邮件")


class PermissionSchema(BaseModel):
    id: int = Field(description="权限ID")
    name: str = Field(description="权限名称")
    module: str = Field(description="权限所属模块")
    mount: bool = Field(description="是否为挂载权限")


class AdminGroupPermissionSchema(AdminGroupSchema):
    permissions: List[PermissionSchema]


class AdminGroupPermissionPageSchema(BasePageSchema):
    items: List[AdminGroupPermissionSchema]


class GroupBaseSchema(BaseModel):
    name: str = Field(description="用户组名称")
    info: Optional[str] = Field(description="用户组信息")


class CreateGroupSchema(GroupBaseSchema):
    permission_ids: List[int] = Field(description="权限ID列表")

    @validator("permission_ids", each_item=True)
    def check_permission_id(cls, v, values, **kwargs):
        if v <= 0:
            raise ParameterError("权限ID必须大于0")
        return v


class GroupIdWithPermissionIdListSchema(BaseModel):
    group_id: int = Field(description="用户组ID")
    permission_ids: List[int] = Field(description="权限ID列表")

    @validator("permission_ids", each_item=True)
    def check_permission_id(cls, v, values, **kwargs):
        if v <= 0:
            raise ParameterError("权限ID必须大于0")
        return v
