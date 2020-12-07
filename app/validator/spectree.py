from enum import Enum
from app.config.codemsg import MESSAGE
from app.config.codedesc import DESC
from pydantic import BaseModel as _BaseModel, Field
from spectree import Response as _Response
from pydantic.main import Any ,object_setattr,validate_model
from lin.exception import APIException, ParameterError

class BaseModel(_BaseModel):

    def __init__(__pydantic_self__, **data: Any) -> None:
        values, fields_set, validation_error = validate_model(__pydantic_self__.__class__, data)
        if validation_error:
            error_list = validation_error.errors()
            tmp = dict()
            for i in error_list:
                tmp[i.get("loc")[0]] = [i.get("msg")]
            raise ParameterError(tmp)
        object_setattr(__pydantic_self__, '__dict__', values)
        object_setattr(__pydantic_self__, '__fields_set__', fields_set)
        __pydantic_self__._init_private_attributes()


class Response(_Response):

    def __init__(self, *args):
        self.code_models = dict()

        for arg in args:
            if issubclass(arg, BaseModel): 
                fields = arg.__fields__
                http_status_code = getattr(fields.get("http_status_code"),"default", None)
                if http_status_code:
                    del fields["http_status_code"]
                else:
                    http_status_code = 200
                self.code_models[http_status_code]  = arg
            elif issubclass(arg, APIException):
                self.code_models[arg.code]  = type(
                    arg.__name__ + 'BaseModel',
                    (BaseModel,),
                    dict(code=arg.message_code , message=MESSAGE.get(arg.message_code, arg.message))
                    )
            else:
                raise ValueError("只接受BaseModel和APIException的子类")

    def generate_spec(self):
        """
        generate the spec for responses

        :returns: JSON
        """
        responses = {}
        for code, base_model in self.code_models.items():
            responses[code] = {
                "description": DESC[code],
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{base_model.__name__}"}
                    }
                },
            }

        return responses




class Query(BaseModel):
    text: str = "default query strings"

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
    summary:str

    class Config:
        schema_extra = {
            "example": {
                "title": "book title",
                "author": "book author",
                "image": "book image",
                "summary": "book summary"
            }
        }

class Language(str, Enum):
    en = "en-US"
    zh = "zh-CN"


class Header(BaseModel):
    Lang: Language


class Cookie(BaseModel):
    key: str
