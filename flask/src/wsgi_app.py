from gevent import monkey


monkey.patch_all()


import psycogreen.gevent


psycogreen.gevent.patch_psycopg()

from src.app import app  # noqa: F401
