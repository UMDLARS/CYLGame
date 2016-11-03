from __future__ import print_function
import ujson
import flask
import flask_classful
import flaskext.markdown as flask_markdown
from Game import GameRunner
from Game import GameLanguage
from Database import GameDB


def get_public_ip():
    # This is taken from: http://stackoverflow.com/a/1267524
    import socket
    return [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]


class GameServer(flask_classful.FlaskView):
    game = None
    url = None
    host = None
    compression = None
    language = None
    avg_game_count = None
    gamedb = None
    route_base = '/'

    @classmethod
    def __load_language(cls):
        if cls.language == GameLanguage.LITTLEPY:
            from littlepython import Compiler
            cls.compiler = Compiler()
        else:
            raise Exception("Invalid language. Could not load hookers.")

    @classmethod
    def __verify_game(cls):
        # TODO: add asserts for every attr used later.
        assert hasattr(cls.game, "GAME_TITLE")
        score_op = getattr(cls.game, "get_score", None)
        assert callable(score_op)

    @flask_classful.route('/scoreboard', methods=["POST"])
    def scoreboard(self):
        token = flask.request.get_json(silent=True).get('token', '')
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        school_tk = self.gamedb.get_school_for_token(token)
        obj = {"school": self.gamedb.get_name(school_tk), "scores": []}
        for user_tk in self.gamedb.get_tokens_for_school(school_tk):
            score = self.gamedb.get_avg_score(user_tk)
            if score is not None:
                obj["scores"] += [{"name": self.gamedb.get_name(user_tk), "score": self.gamedb.get_avg_score(user_tk)}]
        return ujson.dumps(obj)

    @flask_classful.route('/sim_avg', methods=['POST'])
    def sim_avg(self):
        # TODO: create this to run the game 100 times returning the average score to the user.
        code = flask.request.get_json(silent=True).get('code', '')
        token = flask.request.get_json(silent=True).get('token', '')
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        try:
            prog = self.compiler.compile(code.split("\n"))
        except:
            return flask.jsonify(error="Code did not compile")
        runner = GameRunner(self.game, prog)
        try:
            score = runner.run_for_avg_score(times=self.avg_game_count)
            self.gamedb.save_avg_score(token, score)
            self.gamedb.save_code(token, code)
            return flask.jsonify(score=score)
        except Exception as e:
            print(e)
            return flask.jsonify(error="Your bot ran into an error at runtime")
        return result

    @flask_classful.route('/sim', methods=['POST'])
    def sim(self):
        code = flask.request.get_json(silent=True).get('code', '')
        try:
            prog = self.compiler.compile(code.split("\n"))
        except:
            return flask.jsonify(error="Code did not compile")
        runner = GameRunner(self.game, prog)
        try:
            result = ujson.dumps(runner.run_for_playback())
        except Exception as e:
            print(e)
            return flask.jsonify(error="Your bot ran into an error at runtime")
        return result

    # @self.app.route('/')
    def index(self):
        return flask.render_template('index.html', game_title=self.game.GAME_TITLE,
                                example_bot=self.game.default_prog_for_bot(self.language), char_width=self.game.CHAR_WIDTH,
                                char_height=self.game.CHAR_HEIGHT, screen_width=self.game.SCREEN_WIDTH,
                                screen_height=self.game.SCREEN_HEIGHT, base_url=self.url,
                                intro_text=GameLanguage.get_language_description(self.language),
                                char_set=self.game.CHAR_SET)

    @classmethod
    def serve(cls, game, url="http://localhost:5000/", host=None, compression=False, language=GameLanguage.LITTLEPY,
              avg_game_count=10, game_data_path="temp_game"):
        cls.game = game
        cls.url = url
        cls.host = host
        cls.compression = compression
        cls.language = language
        cls.avg_game_count = avg_game_count
        cls.gamedb = GameDB(game_data_path)

        # Make sure that the url ends with a slash
        if cls.url[-1] != "/":
            cls.url += "/"

        cls.app = flask.Flask(__name__.split('.')[0])
        flask_markdown.Markdown(cls.app)
        if cls.compression:
            import flask_compress
            flask_compress.Compress(cls.app)
        cls.register(cls.app)
        cls.__load_language()
        if cls.host:
            cls.app.run(cls.host)
        else:
            cls.app.run()


# This is for backwards compatibility
serve = GameServer.serve
