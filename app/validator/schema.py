from enum import Enum
from inspect import Parameter
from typing import Any, List, Optional

from flask import g
from lin import BaseModel
from lin.exception import ParameterError
from pydantic import Field

datetime_regex = "^((([1-9][0-9][0-9][0-9]-(0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|(20[0-3][0-9]-(0[2469]|11)-(0[1-9]|[12][0-9]|30))) (20|21|22|23|[0-1][0-9]):[0-5][0-9]:[0-5][0-9])$"


class QuerySearchSchema(BaseModel):
    name: Optional[str] = None
    q: Optional[str] = None
    # 2018-11-01 09:39:35
    start: Optional[str] = Field(
        None, regex=datetime_regex, description="YY-MM-DD HH:MM:SS"
    )
    end: Optional[str] = Field(
        None, regex=datetime_regex, description="YY-MM-DD HH:MM:SS"
    )
    count: int = Field(5, gt=0, lt=16, description="0 < count < 16")
    page: int = 0

def g_params_handler(req, resp, req_validation_error, instance):
    schemas = ["cookies","headers","query","json"]
    for schema in schemas:
        params = getattr(req.context, schema)
        if params:
            for k, v in params:
                if hasattr(g, k):
                    raise ParameterError("parameter name {k} in {schema} is Duplicated ".format(schema=schema,k=k))
                setattr(g, k, v)
    g.offset = req.context.query.count * req.context.query.page


class LogSchema(BaseModel):
    id:int
    message :str
    user_id :int
    username :str
    status_code :int
    method :str
    path :str
    permission :str

class BaseListSchema(BaseModel):
    page:int
    count:int
    total:int
    total_page:int
    items:List[Any]

class LogListSchema(BaseListSchema):
    items:List[LogSchema]
    
    
class AccessTokenSchema(BaseModel):
    Authorization: str


class BookResp(BaseModel):
    label: int
    score: float = Field(
        ...,
        gt=0,
        lt=1,
    )


class BookSchema(BaseModel):
    title: str
    author: str
    image: str
    summary: str


class BookListSchema(BaseModel):
    items: List[BookSchema] = []


class Language(str, Enum):
    en = "en-US"
    zh = "zh-CN"
