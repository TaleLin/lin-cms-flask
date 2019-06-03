from flask import current_app
from werkzeug.utils import secure_filename

from lin.core import File
from lin.file import Uploader


class LocalUploader(Uploader):

    def upload(self):
        ret = []
        site_domain = current_app.config.get('SITE_DOMAIN')\
            if current_app.config.get('SITE_DOMAIN') else 'http://127.0.0.1:5000'
        for single in self._file_storage:
            file_md5 = self._generate_md5(single.read())
            single.seek(0)
            exists = File.query.filter_by(md5=file_md5).first()
            if exists:
                ret.append({
                    "key": single.name,
                    "id": exists.id,
                    "url": site_domain + '/assets/' + exists.path
                })
            else:
                absolute_path, relative_path, real_name = self._get_store_path(single.filename)
                secure_filename(single.filename)
                single.save(absolute_path)
                file = File.create_file(
                    name=real_name,
                    path=relative_path,
                    extension=self._get_ext(single.filename),
                    size=self._get_size(single),
                    md5=file_md5,
                    commit=True
                )
                ret.append({
                    "key": single.name,
                    "id": file.id,
                    "url": site_domain + '/assets/' + file.path
                })
        return ret
