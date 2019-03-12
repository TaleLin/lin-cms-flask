from lin.forms import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange


class PoemListForm(Form):
    count = IntegerField()
    author = StringField(validators=[Optional()])

    def validate_count(self, row):
        if not row.data:
            return True
        if int(row.data) > 100 or int(row.data) < 1:
            raise ValueError('必须在1~100之间取值')


class PoemSearchForm(Form):
    q = StringField(validators=[
        DataRequired(message='必须传入搜索关键字')
    ])
