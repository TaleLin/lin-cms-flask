"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask import request

from app.extension.file.local_uploader import LocalUploader
from app.lin.jwt import login_required
from app.lin.redprint import Redprint

file_api = Redprint("file")


@file_api.route("", methods=["POST"])
@login_required
def post_file():
    files = request.files
    uploader = LocalUploader(files)
    ret = uploader.upload()
    return ret
