# 插件demo（古诗展示插件：poem）

> 在大家已经了解了插件机制后，我们按照插件开发规范开发了一个古诗展示插件，在这个demo中，你会学习到一个简单插件的整个开发流程和注意事项

### 插件目录结构

```bash
├───poem
│   │   config.py  // 配置文件（必需），记录关于插件的可用配置
│   │   README.md  // 插件文档
│   │
│   └───app     // 应用开发目录
│           controller.py  // 控制层文件
│           forms.py       // 校验层文件
│           model.py       // 模型层文件
│           __init__.py    // 导出文件（必需）。重要！！！
```

## 定义路由
首先我们在控制层文件`controller.py`中定义一个红图，并且定义两个视图函数
```python
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
    form = PoemSearchForm().validate_for_api()  # 调用数据校验层校验类校验用户传递过来的参数
    poems = Poem().search(form.q.data)
    return jsonify(poems)
```

## 定义数据库模型类
`poem`插件的实现的业务需要依托数据库，所以我们下面需要在模型层文件设计一个名为`Poem`的模型类
```python
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer


class Poem(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False, comment='标题')
    author = Column(String(50), default='未名', comment='作者')
    dynasty = Column(String(50), default='位置', comment='朝代')
    content = Column(String(255), nullable=False, comment='内容')
    
    ...
```

## 定义数据校验类
当我们需要校验用户传递过来的参数时，别忘了数据校验层的存在，我们在`forms.py`中定义一个简单的数据校验类`PoemSearchForm`。并在视图函数中调用。
```python
from lin.forms import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class PoemSearchForm(Form):
    q = StringField(validators=[
        DataRequired(message='必须传入搜索关键字')
    ])

```

## 导出文件
基本业务逻辑已经实现，最关键的一步还要导出文件，也就是在`poem/app/__init__.py`中写入要被Lin的加载器自动加载的红图api和数据模型类
```python
from .controller import api
from .model import Poem
```

## 用配置开启插件
> 最后，在`app/config/setting.py`中添加如下配置:

```python
# setting.py

PLUGIN_PATH = {
    'poem': {'path': 'app.plugins.poem', 'enable': True},
}
```
对于该配置项的含义，已经在[插件使用]一小节详细介绍。

至此，这个简单插件的开发已经完成了。运行项目，我们会发现收据库中会出现我们所创建的poem表。下面请打开fake.py，替换成下面的代码并执行，向表中添加一些初始数据。
```python
from app.app import create_app
from app.plugins.poem.app.model import Poem
from lin.db import db

app = create_app()
with app.app_context():
    with db.auto_commit():
        # 添加诗歌
        poem1 = Poem()
        poem1.title = '夜宿山寺'
        poem1.author = '李白'
        poem1.dynasty = '唐代'
        poem1.content = '危楼高百尺，手可摘星辰。不敢高声语，恐惊天上人。'
        db.session.add(poem1)

        poem2 = Poem()
        poem2.title = '视刀环歌'
        poem2.author = '刘禹锡'
        poem2.dynasty = '唐代'
        poem2.content = '常恨言语浅，不如人意深。今朝两相视，脉脉万重心。'
        db.session.add(poem2)

        poem3 = Poem()
        poem3.title = '己亥杂诗 · 其五'
        poem3.author = '龚自珍'
        poem3.dynasty = '清代'
        poem3.content = '浩荡离愁白日斜，吟鞭东指即天涯。落红不是无情物，化作春泥更护花。'
        db.session.add(poem3)

        poem4 = Poem()
        poem4.title = '杨柳枝'
        poem4.author = '温庭筠'
        poem4.dynasty = '唐代'
        poem4.content = '井底点灯深烛伊，共郎长行莫围棋。玲珑骰子安红豆，入骨相思知不知。'
        db.session.add(poem4)
```

## 用postman调试接口

### 获取所有诗词
URL 
>GET http://localhost:5000/plugin/poem/demo/all

Response 200:
```json
[
    {
        "author": "李白",
        "content": "危楼高百尺，手可摘星辰。不敢高声语，恐惊天上人。",
        "create_time": 1548422493000,
        "dynasty": "唐代",
        "id": 1,
        "title": "夜宿山寺"
    },
    {
        "author": "刘禹锡",
        "content": "常恨言语浅，不如人意深。今朝两相视，脉脉万重心。",
        "create_time": 1548422493000,
        "dynasty": "唐代",
        "id": 2,
        "title": "视刀环歌"
    },
    {
        "author": "龚自珍",
        "content": "浩荡离愁白日斜，吟鞭东指即天涯。落红不是无情物，化作春泥更护花。",
        "create_time": 1548422493000,
        "dynasty": "清代",
        "id": 3,
        "title": "己亥杂诗 · 其五"
    },
    {
        "author": "温庭筠",
        "content": "井底点灯深烛伊，共郎长行莫围棋。玲珑骰子安红豆，入骨相思知不知。",
        "create_time": 1548422493000,
        "dynasty": "唐代",
        "id": 4,
        "title": "杨柳枝"
    }
]
```

### 按标题搜索诗词
URL
>GET http://localhost:5000/plugin/poem/demo/search?q=<string>

Response 200:
```json
[
    {
        "author": "龚自珍",
        "content": "浩荡离愁白日斜，吟鞭东指即天涯。落红不是无情物，化作春泥更护花。",
        "create_time": 1548422493000,
        "dynasty": "清代",
        "id": 3,
        "title": "己亥杂诗 · 其五"
    }
]
```
