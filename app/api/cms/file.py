"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
from flask import request, jsonify
from lin import login_required
from lin.redprint import Redprint

from app.extensions.file.local_uploader import LocalUploader

file_api = Redprint('file')


@file_api.route('', methods=['POST'])
@login_required
def post_file():
    files = request.files
    uploader = LocalUploader(files)
    ret = uploader.upload()
    return jsonify(ret)
