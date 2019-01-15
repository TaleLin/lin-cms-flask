"""
    :copyright: © 2019 by the Lin team.
    :license: MIT, see LICENSE for more details.
"""
import time

from flask import Response, jsonify
from flask_jwt_extended import get_current_user

from lin import db
from lin.core import route_meta, Event
from lin.exception import NotFound, Success
from lin.jwt import group_required, admin_required
from lin.redprint import Redprint
from lin.notify import MESSAGE_EVENTS
from lin.sse import sser
from app.validators.forms import EventsForm

notify_api = Redprint('notify')


@notify_api.route('/', methods=['GET'], strict_slashes=False)
@route_meta(auth='消息推送', module='推送', mount=False)
@group_required
def stream():
    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers=[('Cache-Control', 'no-cache'), ('Connection', 'keep-alive')]
    )


@notify_api.route('/events', methods=['GET'])
@route_meta(auth='获得events', module='推送', mount=False)
@group_required
def get_events():
    current_user = get_current_user()
    if current_user.is_super:
        return jsonify({'events': list(MESSAGE_EVENTS)})
    event = Event.query.filter_by(group_id=current_user.group_id, soft=False).first()
    if event is None:
        raise NotFound(msg='当前用户没有推送项')
    events = event.message_events.split(',')
    return jsonify({'events': events})


@notify_api.route('/events', methods=['POST'])
@route_meta(auth='创建events', module='推送', mount=False)
@admin_required
def create_events():
    form = EventsForm().validate_for_api()
    event = Event.query.filter_by(group_id=form.group_id.data, soft=False).first()
    if event:
        raise NotFound(msg='当前权限组已存在推送项')
    with db.auto_commit():
        ev = Event()
        ev.group_id = form.group_id.data
        ev.message_events = ','.join(form.events.data)
    return Success(msg='创建成功')


@notify_api.route('/events', methods=['PUT'])
@route_meta(auth='更新events', module='推送', mount=False)
@admin_required
def put_events():
    form = EventsForm().validate_for_api()
    event = Event.query.filter_by(group_id=form.group_id.data, soft=False).first()
    if event is None:
        raise NotFound(msg='当前权限组不存在推送项')
    with db.auto_commit():
        event.message_events = ','.join(form.events.data)
    return Success(msg='更新成功')


def event_stream():
    while True:
        if sser.exit_message():
            yield sser.pop()
        else:
            yield sser.heartbeat()
            # 每个5秒发送一次心跳
            time.sleep(5)
