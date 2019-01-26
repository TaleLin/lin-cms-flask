"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

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
