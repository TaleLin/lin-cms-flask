from flask import jsonify, request
import os
from lin.exception import Success, ParameterException, Failed
from .oss import upload_image_bytes
from .model import Image
from .enums import LocalOrCloud
from lin.db import db
from lin.redprint import Redprint
from lin.core import lin_config

api = Redprint('oss')


@api.route('/upload_to_local', methods=['POST'])
def upload():
    image = request.files.get('image', None)
    if not image:
        raise ParameterException(msg='没有找到图片')
    if image and allowed_file(image.filename):
        path = os.path.join(lin_config.get_config('oss.upload_folder'), image.filename)
        image.save(path)
    else:
        raise ParameterException(msg='图片类型不允许或图片key不合法')
    return Success()


@api.route('/upload_to_ali', methods=['POST'])
def upload_to_ali():
    image = request.files.get('image', None)
    if not image:
        raise ParameterException(msg='没有找到图片')
    if image and allowed_file(image.filename):
        url = upload_image_bytes(image.filename, image)
        if url:
            res = {
                'url': url
            }
            with db.auto_commit():
                exist = Image.get(url=url)
                if not exist:
                    data = {
                        'from': LocalOrCloud.CLOUD.value,
                        'url': url
                    }
                    one = Image.create(**data)
                    db.session.flush()
                    res['id'] = one.id
                else:
                    res['id'] = exist.id
            return jsonify(res)
    return Failed(msg='上传图片失败，请检查图片路径')


@api.route('/upload_multiple', methods=['POST'])
def upload_multiple_to_ali():
    imgs = []
    for item in request.files:
        img = request.files.get(item, None)
        if not img:
            raise ParameterException(msg='没接收到图片，请检查图片路径')
        if img and allowed_file(img.filename):
            url = upload_image_bytes(img.filename, img)
            if url:
                # 每上传成功一次图片需记录到数据库
                with db.auto_commit():
                    exist = Image.get(url=url)
                    if not exist:
                        data = {
                            'from': LocalOrCloud.CLOUD.value,
                            'url': url
                        }
                        res = Image.create(**data)
                        db.session.flush()
                        imgs.append({
                            'key': item,
                            'url': url,
                            'id': res.id
                        })
                    else:
                        imgs.append({
                            'key': item,
                            'url': url,
                            'id': exist.id
                        })
    return jsonify(imgs)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in lin_config.get_config('oss.allowed_extensions', [])
