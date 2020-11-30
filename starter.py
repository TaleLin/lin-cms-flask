"""
        :copyright: © 2020 by the Lin team.
        :license: MIT, see LICENSE for more details.
    """

import click
from flask.cli import AppGroup

from app.app import create_app
from app.cli.db import fake as _db_fake
from app.cli.db import init as _db_init
from app.cli.plugin import generate as _plugin_generate
from app.cli.plugin import init as _plugin_init
from app.model.lin import (
    Group,
    GroupPermission,
    Permission,
    User,
    UserGroup,
    UserIdentity,
)

app = create_app(
    group_model=Group,
    user_model=User,
    group_permission_model=GroupPermission,
    permission_model=Permission,
    identity_model=UserIdentity,
    user_group_model=UserGroup,
)

db_cli = AppGroup("db")

plugin_cli = AppGroup("plugin")


@app.route("/", methods=["GET"], strict_slashes=False)
def lin_slogan():
    return """<style type="text/css">*{ padding: 0; margin: 0; } div{ padding: 4px 48px;} a{color:#2E5CD5;cursor:
    pointer;text-decoration: none} a:hover{text-decoration:underline; } body{ background: #fff; font-family:
    "Century Gothic","Microsoft yahei"; color: #333;font-size:18px;} h1{ font-size: 100px; font-weight: normal;
    margin-bottom: 12px; } p{ line-height: 1.6em; font-size: 42px }</style><div style="padding: 24px 48px;"><p>
    Lin <br/><span style="font-size:30px">心上无垢，林间有风。</span></p></div> """


@db_cli.command("init")
@click.option("--force", is_flag=True, help="Create after drop.")
def db_init(force):
    """
    initialize the database.
    """
    if force:
        click.confirm("此操作将清空数据，是否继续?", abort=True)
    _db_init(force)
    click.echo("数据库初始化成功")


@db_cli.command("fake")
def db_fake():
    """
    fake the db data.
    """
    _db_fake()
    click.echo("fake数据添加成功")


@plugin_cli.command("init", with_appcontext=False)
def plugin_init():
    """
    initialize plugin
    """
    _plugin_init()


@plugin_cli.command("generate", with_appcontext=False)
@click.argument("name")
def plugin_generate(name: str):
    """
    generate plugin
    """
    _plugin_generate(name)


app.cli.add_command(db_cli)
app.cli.add_command(plugin_cli)
