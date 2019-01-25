from lin.forms import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class PoemSearchForm(Form):
    q = StringField(validators=[
        DataRequired(message='必须传入搜索关键字')
    ])
