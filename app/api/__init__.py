"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from spectree import SpecTree
from lin import __version__


openapi = SpecTree("flask",title='Lin-CMS API', version=__version__)