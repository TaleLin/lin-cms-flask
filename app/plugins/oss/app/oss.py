import oss2

from lin.util import get_random_str
from lin.core import lin_config


def upload_image_bytes(name: str, data: bytes):
    access_key_id = lin_config.get_config('oss.access_key_id')
    access_key_secret = lin_config.get_config('oss.access_key_secret')
    auth = oss2.Auth(access_key_id, access_key_secret)
    bucket = oss2.Bucket(auth, lin_config.get_config('oss.endpoint'), lin_config.get_config('oss.bucket_name'))
    suffix = name.split('.')[-1]
    rand_name = get_random_str(15) + '.' + suffix
    res = bucket.put_object(rand_name, data)
    if res.resp.status == 200:
        return res.resp.response.url
    return None
