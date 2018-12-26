import os

from flask import Flask, json, request


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
    app.run()
