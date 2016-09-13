from __future__ import print_function
from flask import Flask, render_template, request, jsonify
from CYLGame import CYLGameRunner
from CYLGame import CYLGameLanguage

app = Flask(__name__)
language = CYLGameLanguage.LITTLEPY

if language == CYLGameLanguage.LITTLEPY:
    from littlepy import Compiler
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
    return jsonify(runner.run())


@app.route('/')
def index():
    global game
    return render_template('index.html', game_title=game.GAME_TITLE, example_bot=game.default_prog_for_bot(language))


def serve(cylgame):
    global game
    game = cylgame
    assert hasattr(cylgame, "GAME_TITLE")
    app.run()
