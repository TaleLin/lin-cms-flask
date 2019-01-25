from flask import jsonify
from lin.redprint import Redprint

from app.plugins.poem.app.forms import PoemSearchForm
from .model import Poem

api = Redprint('demo')


@api.route('/all', methods=['GET'])
def get_list():
    poems = Poem().get_all()
    return jsonify(poems)


@api.route('/search', methods=['GET'])
def search():
    form = PoemSearchForm().validate_for_api()
    poems = Poem().search(form.q.data)
    return jsonify(poems)
