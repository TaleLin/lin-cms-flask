"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from app.app import create_app
from tests.utils import get_token

app = create_app()


def test_create():
    with app.test_client() as c:
        rv = c.post('/v1/book/', json={
            'title': '论如何做单测',
            'author': 'pedro',
            'summary': '在写这章之前，笔者一直很踌躇，因为我并没有多年的开发经验，甚至是一年都没有。换言之，我还没有一个良好的软件开发习惯，没有一个标准的开发约束，如果你和我一样，那么请你一定要仔细阅读本小节，并且开始尝试认真，仔细的做单测，它将会让你受益匪浅。',
            'image': 'https://img3.doubanio.com/lpic/s1470003.jpg'
        })
        json_data = rv.get_json()
        print(json_data)
        assert json_data['msg'] == '新建图书成功'
        assert rv.status_code == 201


def test_update():
    with app.test_client() as c:
        rv = c.put('/v1/book/7', json={
            'title': '论如何做单测',
            'author': 'pedro & erik',
            'summary': '在写这章之前，笔者一直很踌躇，因为我并没有多年的开发经验，甚至是一年都没有。换言之，我还没有一个良好的软件开发习惯，没有一个标准的开发约束，如果你和我一样',
            'image': 'https://img3.doubanio.com/lpic/s1470003.jpg'
        })
        json_data = rv.get_json()
        print(json_data)
        assert json_data['msg'] == '更新图书成功'
        assert rv.status_code == 201


def test_delete():
    with app.test_client() as c:
        rv = c.delete('/v1/book/7', headers={
            'Authorization': 'Bearer ' + get_token()
        })
        json_data = rv.get_json()
        print(json_data)
        assert json_data['msg'] == '删除图书成功'
        assert rv.status_code == 201


def test_get_books():
    with app.test_client() as c:
        rv = c.get('/v1/book/')
        json_data = rv.get_json()
        print(json_data)
        assert rv.status_code == 200
