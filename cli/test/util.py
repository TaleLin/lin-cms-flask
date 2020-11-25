import json


def write_token(data):
    obj = json.dumps(data)
    with open('token.json', 'w') as f:
        f.write(obj)


def get_token(key='access_token'):
    with open('token.json', 'r') as f:
        obj = json.loads(f.read())
        return obj[key]
