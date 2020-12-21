"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import os
from uuid import uuid4

from lin import SpecTree

if os.getenv("FLASK_ENV", "production") == "production":
    # spectree 暂未提供关闭文档功能，production部署变更随机路径
    api = SpecTree(
        backend_name="flask",
        title="Lin-CMS API",
        mode="strict",
        version="0.3.0a7",
        path="/".join(str(uuid4()).split("-")),
    )
else:
    api = SpecTree(
        backend_name="flask",
        title="Lin-CMS API",
        mode="strict",
        version="0.3.0a7",
    )
