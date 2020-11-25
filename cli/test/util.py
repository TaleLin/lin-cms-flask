import json


def get_file_path():
    import os
    current_path = os.path.abspath(__file__)
    # 获取当前文件的父目录
    father_path = os.path.abspath(
        os.path.dirname(current_path) + os.path.sep + ".")
    return father_path + os.path.sep + "token.json"


def write_token(data):
    obj = json.dumps(data)
    with open(get_file_path(), 'w') as f:
        f.write(obj)


def get_token(key='access_token'):
    with open(get_file_path(), 'r') as f:
        obj = json.loads(f.read())
        return obj[key]
