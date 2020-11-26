import json


def get_file_path():
    import os
    pytest_cache_dir_path = os.getcwd() + os.path.sep + ".pytest_cache"
    if not os.path.exists(pytest_cache_dir_path):
        os.makedirs(pytest_cache_dir_path)
    json_file_path = pytest_cache_dir_path + os.path.sep + "test.json"
    return json_file_path


def write_token(data):
    obj = json.dumps(data)
    with open(get_file_path(), 'w') as f:
        f.write(obj)


def get_token(key='access_token'):
    with open(get_file_path(), 'r') as f:
        obj = json.loads(f.read())
        return obj[key]
