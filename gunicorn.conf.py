import os
from gevent import monkey

monkey.patch_all()
import multiprocessing

bind = "0.0.0.0:5000"
pidfile = "/tmp/gunicorn.pid"
accesslog = "/var/log/gunicorn.log"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
daemon = False
debug = False
