"""
    forms of Lin
    ~~~~~~~~~

    forms check the incoming params and data

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from flask import request
from wtforms import Form as WTForm, IntegerField
from wtforms.validators import StopValidation

from .exception import ParameterException


class Form(WTForm):
    def __init__(self):
        data = request.get_json(silent=True)
        args = request.args.to_dict()
        super(Form, self).__init__(data=data, **args)

    def validate_for_api(self):
        valid = super(Form, self).validate()
        if not valid:
            raise ParameterException(msg=self.errors)
        return self


def integer_check(form, field):
    if field.data is None:
        raise StopValidation('输入字段不可为空')
    try:
        field.data = int(field.data)
    except ValueError:
        raise StopValidation('不是一个有效整数')


class LinIntegerField(IntegerField):
    """
    校验一个字段是否为正整数
    """

    def __init__(self, label=None, validators=None, **kwargs):
        if validators is not None and type(validators) == list:
            validators.insert(0, integer_check)
        else:
            validators = [integer_check]
        super(LinIntegerField, self).__init__(label, validators, **kwargs)
