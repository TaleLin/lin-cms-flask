"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask import Blueprint, request

from lin import login_required
from app.extension.file.local_uploader import LocalUploader

file_api = Blueprint("file", __name__)


@file_api.route("", methods=["POST"])
@login_required
def post_file():
    files = request.files
    uploader = LocalUploader(files)
    ret = uploader.upload()
    return ret
