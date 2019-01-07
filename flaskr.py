import os
import pandas as pd
import time

from flask import Flask, json, request
from flask.json import jsonify


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

    # a simple page that says hello
    @app.route('/get_history')
    def get_history():
        df = pd.read_csv('./resource/history.csv')
        messages = []
        for index, row in df.iterrows():
            ts = int(row['TIMESTAMP'])
            tl = time.localtime(ts)
            # 格式化时间
            format_time = time.strftime("%Y-%m-%d %H:%M:%S", tl)
            message = {"ID": str(row['ID']), "TIMESTAMP": str(format_time), "TEXT": str(row['TEXT'])}
            messages.append(message)
        return jsonify(messages)

    @app.route('/put_history', methods=['GET', 'POST'])
    def put_history():
        data = request.get_data()
        j_data = eval(json.loads(data))
        df = pd.read_csv('./resource/history.csv')
        append_series = pd.Series({'ID': j_data['ID'], 'TIMESTAMP': j_data['TIMESTAMP'], 'TEXT': j_data['TEXT']})
        df = df.append(append_series, ignore_index=True)
        df.to_csv('./resource/history.csv')
        return "success"

    @app.route('/test_connect')
    def test_connect():
        return "success"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
