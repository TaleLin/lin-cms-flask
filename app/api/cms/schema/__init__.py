import re
from datetime import datetime
from typing import List, Optional

from flask import g
from pydantic import Field, validator

from lin import BaseModel
from app.schema import BasePageSchema, datetime_regex


class UsernameListSchema(BaseModel):
    items: List[str]


class LogQuerySearchSchema(BaseModel):
    keyword: Optional[str] = None
    name: Optional[str] = None
    start: Optional[str] = Field(None, description="YY-MM-DD HH:MM:SS")
    end: Optional[str] = Field(None, description="YY-MM-DD HH:MM:SS")
    count: int = Field(5, gt=0, lt=16, description="0 < count < 16")
    page: int = 0

    @validator("start", "end")
    def datetime_match(cls, v, values, **kwargs):
        if re.match(datetime_regex, v):
            return v
        raise ValueError("时间格式有误")

    @staticmethod
    def offset_handler(req, resp, req_validation_error, instance):
        g.offset = req.context.query.count * req.context.query.page


class LogSchema(BaseModel):
    message: str
    user_id: int
    username: str
    status_code: int
    method: str
    path: str
    permission: str
    time: datetime = Field(alias="create_time")


class LogPageSchema(BasePageSchema):
    items: List[LogSchema]


class LoginSchema(BaseModel):
    username: str = Field(description="用户名")
    password: str = Field(description="密码")
    captcha: Optional[str] = Field(description="验证码")


class AccessTokenSchema(BaseModel):
    __root__: str = Field(description="access_token")


class RefreshTokenSchema(BaseModel):
    __root__: str = Field(description="refresh_token")


class LoginTokenSchema(BaseModel):
    access_token: AccessTokenSchema
    refresh_token: RefreshTokenSchema
