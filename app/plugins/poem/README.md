# 古诗词插件接口文档

>本接口文档仅供插件开发者阅读，如果你想学习如何开发此插件，请阅读
[插件开发](http://doc.cms.7yue.pro/lin/server/plugin_create.html)

## 获取所有诗词接口
URL:
>GET http://localhost:5000/plugin/poem/demo/all

Parameters:
- count: （可选）获取的数量，最小1，最大100，默认5
- author: （可选）按照作者查找，作者列表从获取所有作者API获取

Response:
```json
[
    {
        "author": "苏轼",
        "content": "一别都门三改火/天涯踏尽红尘/依然一笑作春温/无波真古井/有节是秋筠/惆怅孤帆连夜发/送行淡月微云/尊前不用翠眉颦/人生如逆旅/我亦是行人",
        "create_time": 1549438754000,
        "dynasty": "宋代",
        "id": 2,
        "image": "",
        "title": "临江仙·送钱穆父"
    },
    {
        "author": "苏轼",
        "content": "花褪残红青杏小/燕子飞时/绿水人家绕/枝上柳绵吹又少/天涯何处无芳草/墙里秋千墙外道/墙外行人/墙里佳人笑/笑渐不闻声渐悄/多情却被无情恼",
        "create_time": 1549438754000,
        "dynasty": "宋代",
        "id": 8,
        "image": "",
        "title": "蝶恋花·春景"
    }
]
```


## 获取所有作者接口
URL:
>GET http://localhost:5000/plugin/poem/authors

Response:
```json
[
    "元稹",
    "晏殊",
    "欧阳修",
    "纳兰性德",
    "苏轼",
    "薛涛"
]
```

## 搜索诗词接口
>GET http://localhost:5000/plugin/poem/search?q=浣溪沙

Parameters:
- q: （必填）查询关键字

Response:
```json
[
    {
        "author": "晏殊",
        "content": "一曲新词酒一杯/去年天气旧亭台/夕阳西下几时回/无可奈何花落去/似曾相识燕归来/小园香径独徘徊",
        "create_time": 1549438754000,
        "dynasty": "宋代",
        "id": 6,
        "image": "",
        "title": "浣溪沙·一曲新词酒一杯"
    },
    {
        "author": "纳兰性德",
        "content": "残雪凝辉冷画屏/落梅横笛已三更/更无人处月胧明/我是人间惆怅客/知君何事泪纵横/断肠声里忆平生",
        "create_time": 1549438754000,
        "dynasty": "清代",
        "id": 7,
        "image": "",
        "title": "浣溪沙·残雪凝辉冷画屏"
    }
]
```
