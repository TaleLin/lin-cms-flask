import base64
import io
import random
import string
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


class CaptchaTool:
    """
    生成图片验证码
    """

    def __init__(self, width=50, height=12):

        self.width = width
        self.height = height
        # 新图片对象
        self.im = Image.new("RGB", (width, height), "white")
        # 字体
        self.font = ImageFont.load_default()
        # draw对象
        self.draw = ImageDraw.Draw(self.im)

    def draw_lines(self, num=3):
        """
        划线
        """
        for num in range(num):
            x1 = random.randint(0, self.width / 2)
            y1 = random.randint(0, self.height / 2)
            x2 = random.randint(0, self.width)
            y2 = random.randint(self.height / 2, self.height)
            self.draw.line(((x1, y1), (x2, y2)), fill="black", width=1)

    def get_verify_code(self) -> Tuple[bytes, str]:
        """
        生成验证码图形
        """
        # 设置随机4位数字验证码
        code = "".join(random.sample(string.digits, 4))
        # 绘制字符串
        for item in range(4):
            self.draw.text(
                (6 + random.randint(-3, 3) + 10 * item, 2 + random.randint(-2, 2)),
                text=code[item],
                fill=(
                    random.randint(32, 127),
                    random.randint(32, 127),
                    random.randint(32, 127),
                ),
                font=self.font,
            )
        # 划线
        # self.draw_lines()
        # 重新设置图片大小
        self.im = self.im.resize((80, 30))
        # 图片转为base64字符串
        buffered = io.BytesIO()
        self.im.save(buffered, format="webp")
        img = b"data:image/png;base64," + base64.b64encode(buffered.getvalue())
        return img, code
