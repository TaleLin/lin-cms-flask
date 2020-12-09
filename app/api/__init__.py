"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from lin import __version__
from spectree import SpecTree

openapi = SpecTree(
    backend_name="flask", title="Lin-CMS API", mode="strict", version=__version__
)
