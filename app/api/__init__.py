"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from functools import wraps
from flask import g
from lin import __version__, BaseModel
from lin.exception import ParameterError
from spectree import SpecTree as _SpecTree

class SpecTree(_SpecTree):
    def validate(
        self,
        query=None,
        json=None,
        headers=None,
        cookies=None,
        resp=None,
        tags=(),
        before=None,
        after=None,
    ):
        """
        - validate query, json, headers in request
        - validate response body and status code
        - add tags to this API route

        :param query: `pydantic.BaseModel`, query in uri like `?name=value`
        :param json: `pydantic.BaseModel`, JSON format request body
        :param headers: `pydantic.BaseModel`, if you have specific headers
        :param cookies: `pydantic.BaseModel`, if you have cookies for this route
        :param resp: `spectree.Response`
        :param tags: a tuple of tags string
        :param before: :meth:`spectree.utils.default_before_handler` for specific endpoint
        :param after: :meth:`spectree.utils.default_after_handler` for specific endpoint
        """

        def decorate_validation(func):
            @wraps(func)
            def sync_validate(*args, **kwargs):
                def g_params_handler(req, resp, req_validation_error, instance):
                    if before:
                        before(req, resp,req_validation_error,instance)
                    schemas = ["headers","cookies","query","json"]
                    for schema in schemas:
                        params = getattr(req.context, schema)
                        if params:
                            for k, v in params:
                                if hasattr(g, k):
                                    raise ParameterError({k:"This parameter in {schema} needs to be renamed".format(schema=schema.capitalize())})
                                setattr(g, k, v)
                return self.backend.validate(
                    func,
                    query,
                    json,
                    headers,
                    cookies,
                    resp,
                    g_params_handler,
                    after or self.after,
                    *args,
                    **kwargs,
                )
            validation = sync_validate

            # register
            for name, model in zip(
                ("query", "json", "headers", "cookies"), (query, json, headers, cookies)
            ):
                if model is not None:
                    assert issubclass(model, BaseModel)
                    self.models[model.__name__] = model.schema()
                    setattr(validation, name, model.__name__)

            if resp:
                for model in resp.models:
                    self.models[model.__name__] = model.schema()
                validation.resp = resp

            if tags:
                validation.tags = tags

            # register decorator
            validation._decorator = self
            return validation

        return decorate_validation
    


apidoc = SpecTree(
    backend_name="flask", title="Lin-CMS API", mode="strict", version=__version__
)
