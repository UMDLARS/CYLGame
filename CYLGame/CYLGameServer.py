from __future__ import print_function
import ujson
from flask import Flask, render_template, request, jsonify
from flask_compress import Compress
from flaskext.markdown import Markdown
from CYLGame import CYLGameRunner
from CYLGame import CYLGameLanguage

app = Flask(__name__)
Markdown(app)
Compress(app)
language = CYLGameLanguage.LITTLEPY

if language == CYLGameLanguage.LITTLEPY:
    from littlepython import Compiler
    compiler = Compiler()


@app.route('/sim', methods=['POST'])
def sim():
    global game
    code = request.get_json(silent=True).get('code', '')
    try:
        prog = compiler.compile(code.split("\n"))
    except:
        return jsonify(error="Code did not compile")
    runner = CYLGameRunner(game, prog)
    try:
        result = ujson.dumps(runner.run())
    except Exception as e:
        print(e)
        return jsonify(error="Your bot ran into an error at runtime")
    return result


@app.route('/')
def index():
    global game, base_url
    return render_template('index.html', game_title=game.GAME_TITLE, example_bot=game.default_prog_for_bot(language), char_width=game.CHAR_WIDTH,
                           char_height=game.CHAR_HEIGHT, screen_width=game.SCREEN_WIDTH, screen_height=game.SCREEN_HEIGHT, base_url=base_url,
                           intro_text=CYLGameLanguage.get_language_description(language), char_set=game.CHAR_SET)


def serve(cylgame, url="http://localhost:5000/", host=None):
    global game, base_url
    if url[-1] != "/":
        url += "/"
    base_url = url
    game = cylgame
    assert hasattr(cylgame, "GAME_TITLE")
    if host:
        app.run(host=host)
    else:
        app.run()
