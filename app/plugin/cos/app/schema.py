from typing import List

from lin import BaseModel


class CosOutSchema(BaseModel):
    id: int
    file_name: str
    file_key: str
    url: str


class CosOutSchemaList(BaseModel):
    __root__: List[CosOutSchema]
