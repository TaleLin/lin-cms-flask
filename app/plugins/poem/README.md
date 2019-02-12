# 古诗词插件接口文档

>本接口文档仅供插件开发者阅读，如果你想学习如何开发此插件，请阅读
[插件开发](http://doc.cms.7yue.pro/lin/server/plugin_create.html)

## 获取所有诗词接口
URL:
>GET http://localhost:5000/plugin/poem/all

Parameters:
- count: （可选）获取的数量，最小1，最大100，默认5
- author: （可选）按照作者查找，作者列表从获取所有作者API获取

Response:
```json
[
    {
        "author": "欧阳修",
        "content": [
            [
                "去年元夜时",
                "花市灯如昼",
                "月上柳梢头",
                "人约黄昏后"
            ],
            [
                "今年元夜时",
                "月与灯依旧",
                "不见去年人",
                "泪湿春衫袖"
            ]
        ],
        "create_time": 1549438754000,
        "dynasty": "宋代",
        "id": 1,
        "image": "",
        "title": "生查子·元夕"
    },
    {
        "author": "苏轼",
        "content": [
            [
                "一别都门三改火",
                "天涯踏尽红尘",
                "依然一笑作春温",
                "无波真古井",
                "有节是秋筠"
            ],
            [
                "惆怅孤帆连夜发",
                "送行淡月微云",
                "尊前不用翠眉颦",
                "人生如逆旅",
                "我亦是行人"
            ]
        ],
        "create_time": 1549438754000,
        "dynasty": "宋代",
        "id": 2,
        "image": "",
        "title": "临江仙·送钱穆父"
    }
]
```

Response_description:
- author: 作者
- content: 内容。是一个二维数组，第一维数组用来区分词的每一阙（如果是古诗，那么第一维数组中只有一个元素），第二维数组用来区分古诗词的每一句。
- create_time: 创建时间
- dynasty: 作者所属朝代
- id: id号码
- image: 配图
- title: 标题


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
