import os
from itertools import groupby
from operator import itemgetter


def split_group(dict_list, key):
    dict_list.sort(key=itemgetter(key))
    tmps = groupby(dict_list, itemgetter(key))
    result = []
    for key, group in tmps:
        result.append({key: list(group)})
    return result


basedir = os.getcwd()
