import os

from redis import Redis
from flask import Response
from flask import Flask, json, request
from redis._compat import xrange


class FileHandler:

    def __init__(self):
        self.path = "./resource/history.txt"

    def get_chat_history(self):
        with open(self.path, "r", encoding="utf-8") as f:
            history_dictionary = {}
            for index, line in enumerate(f.readlines()):
                line.rstrip("\n")
                history_dictionary.__setitem__(str(index), str(line))

            return json.jsonify(history_dictionary)

    def put_chat_history(self, text):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(text+"\n")


import time
from datetime import datetime

redis = Redis(host="localhost",port=6379,decode_responses=True)
ONLINE_LAST_MINUTES = 5

def mark_online(user_id):
    now = int(time.time())
    expires = now + (app.config['ONLINE_LAST_MINUTES'] * 60) + 10
    all_users_key = 'online-users/%d' % (now // 60)
    user_key = 'user-activity/%s' % user_id
    p = redis.pipeline()
    p.sadd(all_users_key, user_id)
    p.set(user_key, now)
    p.expireat(all_users_key, expires)
    p.expireat(user_key, expires)
    p.execute()


def get_user_last_activity(user_id):
    last_active = redis.get('user-activity/%s' % user_id)
    if last_active is None:
        return None
    return datetime.utcfromtimestamp(int(last_active))


def get_online_users():
    current = int(time.time()) // 60
    minutes = xrange(app.config['ONLINE_LAST_MINUTES'])
    return redis.sunion(['online-users/%d' % (current - x)
                         for x in minutes])


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_request
    def mark_current_user_online():
        mark_online(request.remote_addr)

    @app.route('/online')
    def index():
        return Response('Online: %s' % ', '.join(get_online_users()),
                        mimetype='text/plain')

    # a simple page that says hello
    @app.route('/get_history')
    def get_history():
        fh = FileHandler()
        return fh.get_chat_history()

    @app.route('/put_history', methods=['GET', 'POST'])
    def put_history():
        data = request.get_data()
        j_data = json.loads(data)
        text = j_data['0']
        fh = FileHandler()
        fh.put_chat_history(text)
        return "success"

    @app.route('/test_connect')
    def test_connect():
        return "success"

    return app


if __name__ == '__main__':
    app = create_app()
    app.config['ONLINE_LAST_MINUTES'] = ONLINE_LAST_MINUTES
    app.run()
