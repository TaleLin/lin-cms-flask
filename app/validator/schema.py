import re
from enum import Enum
from typing import Any, List, Optional

from flask import g
from lin.apidoc import BaseModel
from pydantic import Field, validator

datetime_regex = "^((([1-9][0-9][0-9][0-9]-(0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|(20[0-3][0-9]-(0[2469]|11)-(0[1-9]|[12][0-9]|30))) (20|21|22|23|[0-1][0-9]):[0-5][0-9]:[0-5][0-9])$"


class AuthorizationSchema(BaseModel):
    Authorization: str


class BookQuerySearchSchema(BaseModel):
    q: Optional[str] = str()


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
    id: int
    message: str
    user_id: int
    username: str
    status_code: int
    method: str
    path: str
    permission: str


class BasePageSchema(BaseModel):
    page: int
    count: int
    total: int
    total_page: int
    items: List[Any]


class LogPageSchema(BasePageSchema):
    items: List[LogSchema]


class BookInSchema(BaseModel):
    title: str
    author: str
    image: str
    summary: str


class BookOutSchema(BaseModel):
    id: int
    title: str
    author: str
    image: str
    summary: str


class BookSchemaList(BaseModel):
    __root__: List[BookOutSchema]


class Language(str, Enum):
    en = "en-US"
    zh = "zh-CN"
