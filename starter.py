"""
    :copyright: © 2020 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""

from app.app import create_app
import click

app = create_app()


@app.route('/', methods=['GET'], strict_slashes=False)
def lin_slogan():
    return """<style type="text/css">*{ padding: 0; margin: 0; } div{ padding: 4px 48px;} a{color:#2E5CD5;cursor:
    pointer;text-decoration: none} a:hover{text-decoration:underline; } body{ background: #fff; font-family:
    "Century Gothic","Microsoft yahei"; color: #333;font-size:18px;} h1{ font-size: 100px; font-weight: normal;
    margin-bottom: 12px; } p{ line-height: 1.6em; font-size: 42px }</style><div style="padding: 24px 48px;"><p>
    Lin <br/><span style="font-size:30px">心上无垢，林间有风。</span></p></div> """


@app.cli.command("db")
@click.argument("op")
def db(op: str):
    '''
    Run database script
    '''
    if op == 'init':
        from cli.db import init
        init()
    if op == 'fake':
        from cli.db import fake
        fake()

@app.cli.command("test")
def test():
    import os
    '''
    Run unit test
    '''
    os.system('pytest')

