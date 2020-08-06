"""
    Redprint of Lin
    ~~~~~~~~~

    Redprint make blueprint more fine-grained

    :copyright: © 2018 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""


class Redprint:
    def __init__(self, name, with_prefix=True):
        self.name = name
        self.with_prefix = with_prefix
        self.mound = []

    def route(self, rule, **options):
        def decorator(f):
            self.mound.append((f, rule, options))
            return f

        return decorator

    def register(self, bp, url_prefix=None):
        if url_prefix is None and self.with_prefix:
            url_prefix = '/' + self.name
        else:
            url_prefix = '' + str(url_prefix) + '/' + self.name
        for f, rule, options in self.mound:
            endpoint = self.name + '+' + options.pop("endpoint", f.__name__)
            if rule:
                url = url_prefix + rule
                bp.add_url_rule(url, endpoint, f, **options)
            else:
                bp.add_url_rule(url_prefix, endpoint, f, **options)
