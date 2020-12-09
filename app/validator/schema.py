from enum import Enum
from typing import List

from lin import BaseModel
from pydantic import Field


class AccessTokenSchema(BaseModel):
    Authorization: str


class SearchBookSchema(BaseModel):
    q: str


class BookResp(BaseModel):
    label: int
    score: float = Field(
        ...,
        gt=0,
        lt=1,
    )


class Data(BaseModel):
    uid: str
    limit: int = 5
    vip: bool

    class Config:
        schema_extra = {
            "example": {
                "uid": "very_important_user",
                "limit": 10,
                "vip": True,
            }
        }


class BookSchema(BaseModel):
    title: str
    author: str
    image: str
    summary: str


class BookListSchema(BaseModel):
    result: List[BookSchema] = []


class Language(str, Enum):
    en = "en-US"
    zh = "zh-CN"


class Header(BaseModel):
    Lang: Language


class Cookie(BaseModel):
    key: str
