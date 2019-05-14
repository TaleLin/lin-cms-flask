import os

from werkzeug.utils import secure_filename

from lin.core import File
from lin.file import Uploader


class LocalUploader(Uploader):

    def upload(self, **kwargs):
        ret = dict(file_storage=self._file_storage, file=[])
        for single in self._file_storage:
            secure_filename(single.filename)
            name = self._generate_uuid() + self._get_ext(single)
            full_path = os.path.join(self._store_dir, name)
            single.save(full_path)
            file = File.create_file(
                name=name,
                path=full_path,
                _type=1,
                extension=self._get_ext(single),
                size=self._get_size(single),
                commit=True
            )
            ret['file'].append(file)
        return ret
