---
title: 开发一个小插件
---

# <H2Icon /> 开发一个小插件（目前处于测试状态）

Lin 的插件很灵活，你可以在本地的 plugins 目录下使用一个插件，或者通过`pip`安装一个插件到 site-packages 中。


> 在大家已经了解了插件机制和插件的使用方法后，本小结我们来手把手带着大家来开发一个简易的古诗词插件，我们选择在本地的`app/plugins`目录下进行开发，你将学到一个插件的整个开发流程和注意事项。好了，话不多说，我们开始吧！

:::tip
定义只涉及前端的插件为`A型插件`，只涉及后端的插件为`B型插件`，需要前后端对接 API 共同完成一个业务逻辑的插件为`AB型插件`。本插件为前后端共同协作的`AB型插件`，所以为了规范统一，请特别注意你们的插件命名一致哦。
:::

## 插件目录结构
在开发前，我们首先来浏览一下插件的目录结构。
在`app/plugins`目录下创建以插件名称命名的目录，我们所开发的示例插件为古诗词展示插件，所以以`poem`来命名。我们在`app/plugins/poem/app`目录下进行插件的开发，其余文件含义请查看下面的注释。
```bash
├───poem
│   │   config.py  // 配置文件（必需），记录关于插件的可用配置
│   │   info.py    // 插件基本信息
│   │   README.md  // 插件文档
│   │
│   └───app     // 应用开发目录
│           controller.py  // 控制层文件
│           forms.py       // 校验层文件
│           model.py       // 模型层文件
│           __init__.py    // 导出文件（必需）。重要！！！
```

## 定义路由
首先，在控制层文件`controller.py`下定义一个红图`redprint`，以及业务相关的视图函数。

```python
from flask import jsonify
from lin.redprint import Redprint

from app.plugins.poem.app.forms import PoemSearchForm
from .model import Poem

api = Redprint('poem')


@api.route('/all', methods=['GET'])
def get_list():
    poems = Poem().get_all()
    return jsonify(poems)

...
```

:::warning
由于本插件只有一个控制器，也就是只有一个`redprint`，那么Lin内核所生成的路由不会有二级前缀，只有一个一级前缀，即/plugin，对此如果你还不够了解，请移步阅读[插件中的路由规范](./plugin_practice.md#上传图片到本地)
:::

## 定义数据库模型类
由于poem插件所实现的业务需要依托数据库，所以我们下面需要在模型层文件设计一个名为Poem的模型类，这里请先检查你的数据库中是否已存在同名表再确认命名。


```python
from lin.core import lin_config
from lin.exception import NotFound
from lin.interface import InfoCrud as Base
from sqlalchemy import Column, String, Integer, Text


class Poem(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False, comment='标题')
    author = Column(String(50), default='未名', comment='作者')
    dynasty = Column(String(50), default='未知', comment='朝代')
    content = Column(Text, nullable=False, comment='内容')
    image = Column(String(255), default='', comment='配图')

    def get_all(self):
        poems = self.query.filter_by(delete_time=None).limit(
            lin_config.get_config('poem.limit')
        ).all()
        if not poems:
            raise NotFound(msg='没有找到相关诗词')
        return poems
```
同样的，本插件只需要一个模型类，如果你所设计的插件需要多个模型类，请定义多个模型层文件。如果你对模型类的开发还不够了解，可以先去学习一下[模型管理]('./authority_and_models.md')小节

## 关于配置文件
在上面的模型层代码中，你或许已经发现，我们从lin的核心库中导入了`lin_config`，并且使用`lin_config.get_config('poem.limit')`获取到了配置，那么配置文件定义在哪里呢？
在插件目录结构中，我们可以发现`config.py`文件的位置。我们打开`config.py`配置文件，可以发现，Lin建议用户定义的配置项是小写的。如果你开发的插件有更多的配置，都可以在这个文件中添加。
```python
# app/plugins/poem/config.py
limit = 20
```

## 定义数据校验类
当我们需要校验用户传递过来的参数时，别忘了数据校验层的存在，我们在`forms.py`中定义一个简单的数据校验类`PoemSearchForm`。并在视图函数中调用。

```python
# app/plugins/poem/app/forms.py
from lin.forms import Form
from wtforms import StringField
from wtforms.validators import DataRequired


class PoemSearchForm(Form):
    q = StringField(validators=[
        DataRequired(message='必须传入搜索关键字')
    ])


# app/plugins/poem/app/controller.py
...

@api.route('/search', methods=['GET'])
def search():
    form = PoemSearchForm().validate_for_api()
    poems = Poem().search(form.q.data)
    return jsonify(poems)

```

## 导出文件

基本业务逻辑已经实现，最关键的一步还要导出文件，也就是在`poem/app/__init__.py`中写入要被 Lin 的`loader`(加载器)自动加载的`红图 api` 和`数据模`型类

```python
# app/plugins/poem/app/__init__.py
from .controller import api
from .model import Poem
```

如果你有多个红图或者多个模型类，同样在这个文件下导入即可，但请注意`不要重名`。

## 用配置开启插件

> 最后，在`app/config/setting.py`中添加如下配置:

```python
# setting.py

PLUGIN_PATH = {
    'poem': {'path': 'app.plugins.poem', 'enable': True, 'limit': 5},
}
```

对于该配置项的含义，已经在[插件使用](./plugin_practice.md)一小节详细介绍。此处设置了limit为5，他的权级会高于上述`config.py`中的权级，所以在调用配置时，会优先调用`setting.py`中的配置。

至此，这个简单插件的全部开发已经完成了。运行starter.py，我们会发现数据库中会出现我们想要创建的`poem`表。下面请打开项目根目录下的fake.py，替换成下面的代码并执行，向该表中添加一些初始数据。

```python
from app.app import create_app
from app.plugins.poem.app.model import Poem
from lin.db import db

app = create_app()
with app.app_context():
    with db.auto_commit():
        # 添加诗歌
        poem1 = Poem()
        poem1.title = '生查子·元夕'
        poem1.author = '欧阳修'
        poem1.dynasty = '宋代'
        poem1.content = """去年元夜时，花市灯如昼。
        月上柳梢头，人约黄昏后。
        今年元夜时，月与灯依旧。
        不见去年人，泪湿春衫袖。"""
        db.session.add(poem1)

        poem2 = Poem()
        poem2.title = '临江仙·送钱穆父'
        poem2.author = '苏轼'
        poem2.dynasty = '宋代'
        poem2.content = """一别都门三改火，天涯踏尽红尘。依然一笑作春温。无波真古井，有节是秋筠。
        惆怅孤帆连夜发，送行淡月微云。尊前不用翠眉颦。人生如逆旅，我亦是行人。"""
        db.session.add(poem2)

        poem3 = Poem()
        poem3.title = '春望词四首'
        poem3.author = '薛涛'
        poem3.dynasty = '唐代'
        poem3.content = """花开不同赏，花落不同悲。
        欲问相思处，花开花落时。
        揽草结同心，将以遗知音。
        春愁正断绝，春鸟复哀吟。
        风花日将老，佳期犹渺渺。
        不结同心人，空结同心草。
        那堪花满枝，翻作两相思。
        玉箸垂朝镜，春风知不知。"""
        db.session.add(poem3)

        poem4 = Poem()
        poem4.title = '长相思'
        poem4.author = '纳兰性德'
        poem4.dynasty = '清代'
        poem4.content = """山一程，水一程，身向榆关那畔行，夜深千帐灯。
        风一更，雪一更，聒碎乡心梦不成，故园无此声。"""
        db.session.add(poem4)

        poem5 = Poem()
        poem5.title = '离思五首·其四'
        poem5.author = '元稹'
        poem5.dynasty = '唐代'
        poem5.content = """曾经沧海难为水，除却巫山不是云。
取次花丛懒回顾，半缘修道半缘君。"""
        db.session.add(poem5)

        poem6 = Poem()
        poem6.title = '浣溪沙·一曲新词酒一杯'
        poem6.author = '晏殊'
        poem6.dynasty = '宋代'
        poem6.content = """一曲新词酒一杯，去年天气旧亭台。夕阳西下几时回？
无可奈何花落去，似曾相识燕归来。小园香径独徘徊。"""
        db.session.add(poem6)

        poem7 = Poem()
        poem7.title = '浣溪沙·残雪凝辉冷画屏'
        poem7.author = '纳兰性德'
        poem7.dynasty = '清代'
        poem7.content = """残雪凝辉冷画屏，落梅横笛已三更，更无人处月胧明。
我是人间惆怅客，知君何事泪纵横，断肠声里忆平生。 """
        db.session.add(poem7)

        poem8 = Poem()
        poem8.title = '蝶恋花·春景'
        poem8.author = '苏轼'
        poem8.dynasty = '宋代'
        poem8.content = """花褪残红青杏小。燕子飞时，绿水人家绕。枝上柳绵吹又少。天涯何处无芳草。
墙里秋千墙外道。墙外行人，墙里佳人笑。笑渐不闻声渐悄。多情却被无情恼。"""
        db.session.add(poem8)
```

## 用poseman调试接口

### 调用获取所有诗词接口
使用GET方法访问`http://localhost:5000/plugin/poem/demo/all`url，将会得到如下数据:
```json
[
    {
        "author": "欧阳修",
        "content": "去年元夜时，花市灯如昼。\n        月上柳梢头，人约黄昏后。\n        今年元夜时，月与灯依旧。\n        不见去年人，泪湿春衫袖。",
        "create_time": 1548581209000,
        "dynasty": "宋代",
        "id": 1,
        "image": "",
        "title": "生查子·元夕"
    },
    {
        "author": "苏轼",
        "content": "一别都门三改火，天涯踏尽红尘。依然一笑作春温。无波真古井，有节是秋筠。\n        惆怅孤帆连夜发，送行淡月微云。尊前不用翠眉颦。人生如逆旅，我亦是行人。",
        "create_time": 1548581209000,
        "dynasty": "宋代",
        "id": 2,
        "image": "",
        "title": "临江仙·送钱穆父"
    },
    {
        "author": "薛涛",
        "content": "花开不同赏，花落不同悲。\n        欲问相思处，花开花落时。\n        揽草结同心，将以遗知音。\n        春愁正断绝，春鸟复哀吟。\n        风花日将老，佳期犹渺渺。\n        不结同心人，空结同心草。\n        那堪花满枝，翻作两相思。\n        玉箸垂朝镜，春风知不知。",
        "create_time": 1548581209000,
        "dynasty": "唐代",
        "id": 3,
        "image": "",
        "title": "春望词四首"
    },
    {
        "author": "纳兰性德",
        "content": "山一程，水一程，身向榆关那畔行，夜深千帐灯。\n        风一更，雪一更，聒碎乡心梦不成，故园无此声。",
        "create_time": 1548581209000,
        "dynasty": "清代",
        "id": 4,
        "image": "",
        "title": "长相思"
    },
    {
        "author": "元稹",
        "content": "曾经沧海难为水，除却巫山不是云。\n取次花丛懒回顾，半缘修道半缘君。",
        "create_time": 1548581209000,
        "dynasty": "唐代",
        "id": 5,
        "image": "",
        "title": "离思五首·其四"
    }
]
```

## 小结

在本节中，我们遵守插件的开发规范，很容易地开发出了古诗词插件的后端API部分，如果你想了解前端插件部分的实际开发，请移步[前端插件](#../client/plugin.md)。
