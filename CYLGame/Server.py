from __future__ import print_function

import multiprocessing
import os
import random
import shutil
import sys
import traceback
from datetime import datetime
from multiprocessing import Process

import flask
import flask_classful
import ujson
from cachetools import LRUCache
from flask import escape, has_request_context
from flask_request_id_header.middleware import RequestID

from CYLGame.Comp import MultiplayerCompRunner, RollingMultiplayerCompRunner

from .Database import GameDB
from .Game import GameLanguage, GameRunner, GridGame, average
from .Log import setup_logging
from .Player import Room
from .Utils import int2base

ANONYMOUS_COMP = "P00000000"
ANONYMOUS_SCHOOL = "S00000000"
ANONYMOUS_USER = "00000000"


def get_public_ip():
    # This is taken from: http://stackoverflow.com/a/1267524
    import socket

    return [
        l
        for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
            [
                [
                    (s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close())
                    for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]
                ][0][1]
            ],
        )
        if l
    ][0][0]


def find_name_from_code(code):
    import re

    name = re.findall(r"#\s*name:\s*(.*)\s*", code, re.IGNORECASE)
    if len(name):
        return name[0]
    else:
        return ""


class GameServer(flask_classful.FlaskView):
    game = None
    host = None
    port = None
    compression = None
    language = None
    avg_game_count = None
    _avg_game_func = None
    charset = None
    gamedb = None
    play_game_cache: LRUCache
    # log: Logger = None
    route_base = "/"

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

    @classmethod
    def __copy_in_charset(cls, charset):
        fonts_dir = os.path.join(cls.gamedb.www_cache.static_dir, "fonts")
        if not os.path.exists(fonts_dir):
            os.mkdir(fonts_dir)
        charset_name = os.path.basename(charset)
        new_charset_path = os.path.join(fonts_dir, charset_name)
        shutil.copyfile(charset, new_charset_path)
        return charset_name

    def before_request(self, name, **kwarg):
        if has_request_context():
            self.app.logger.debug(f"{flask.request.method} {flask.request.url}")
        else:
            self.app.logger.error(f"{name}() called without context.")

    @flask_classful.route("/scoreboard", methods=["POST"])
    def scoreboard(self):
        token = flask.request.get_json(silent=True).get("token", "")
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        school_tk = self.gamedb.get_school_for_token(token)
        obj = {"school": self.gamedb.get_name(school_tk), "scores": []}
        for user_tk in self.gamedb.get_tokens_for_school(school_tk):
            score = self.gamedb.get_avg_score(user_tk)
            if score is not None:
                obj["scores"] += [
                    {"name": escape(self.gamedb.get_name(user_tk)), "score": self.gamedb.get_avg_score(user_tk)}
                ]
        if self.game.MULTIPLAYER:

            def get_game_name(gtoken):
                bot_names = []
                for token in self.gamedb.get_players_for_game(gtoken):
                    bot_names += [self.gamedb.get_name(token)]
                return "{} - '{}'".format(gtoken, "' vs '".join(bot_names))

            gtokens = []
            for gtoken in self.gamedb.get_games_for_token(ANONYMOUS_COMP):
                if token in self.gamedb.get_players_for_game(gtoken):
                    gtokens += [{"token": gtoken, "text": get_game_name(gtoken)}]
            gtokens.sort(key=lambda x: self.gamedb.get_ctime_for_game(x["token"]), reverse=True)
            obj["games"] = gtokens
        return ujson.dumps(obj)

    @flask_classful.route("/comp_scoreboards", methods=["POST"])
    def comp_scoreboards(self):
        token = flask.request.get_json(silent=True).get("token", "").upper()
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        comps = self.gamedb.get_comps_for_token(token)
        obj = {"comps": []}
        for comp in comps:
            comp_obj = {"scores": []}
            for school in self.gamedb.get_schools_in_comp(comp):
                score = self.gamedb.get_comp_avg_score(comp, school)
                if score is not None:
                    comp_obj["scores"] += [{"name": escape(self.gamedb.get_name(school)), "score": score}]
            obj["comps"] += [comp_obj]
        return ujson.dumps(obj)

    @flask_classful.route("/save_code", methods=["POST"])
    def save_code(self):
        code = flask.request.get_json(silent=True).get("code", "")
        token = flask.request.get_json(silent=True).get("token", "").upper()
        options = flask.request.get_json(silent=True).get("options", None)
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")

        self.gamedb.save_code(token, code, options)
        name = find_name_from_code(code)
        if name:
            self.gamedb.save_name(token, name)

        return flask.jsonify(message="success")

    @flask_classful.route("/game/<gtoken>")
    def get_game_data(self, gtoken):
        if not self.gamedb.is_game_token(gtoken):
            return flask.jsonify(error="Invalid Game Token")

        return ujson.dumps(self.gamedb.get_game_frames(gtoken))

    @flask_classful.route("/game/<gtoken>/<token>")
    def get_player_game_data(self, gtoken, token):
        gtoken = gtoken.upper()
        token = token.upper()
        if not self.gamedb.is_game_token(gtoken):
            return flask.jsonify(error="Invalid Game Token")
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid User Token")

        data = self.gamedb.get_game_frames(gtoken)
        data["player"] = self.gamedb.get_player_game_data(gtoken, token)

        if token == ANONYMOUS_USER:
            self.gamedb.delete_game(gtoken)

        return ujson.dumps(data)

    @flask_classful.route("/player")
    def get_player(self):
        if self.game.GRID:
            return flask.render_template(
                "grid_player.html",
                char_width=self.game.CHAR_WIDTH,
                char_height=self.game.CHAR_HEIGHT,
                screen_width=self.game.SCREEN_WIDTH,
                screen_height=self.game.SCREEN_HEIGHT,
                char_set=self.charset,
            )

    @flask_classful.route("/sim_avg", methods=["POST"])
    def sim_avg(self):
        # TODO: create this to run the game 100 times returning the average score to the user.
        code = flask.request.get_json(silent=True).get("code", "")
        token = flask.request.get_json(silent=True).get("token", "").upper()
        options = flask.request.get_json(silent=True).get("options", None)
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        try:
            prog = self.compiler.compile(code)
        except:
            return flask.jsonify(error="Code did not compile")
        if self.game.MULTIPLAYER:
            self.gamedb.save_code(token, code, options)
            name = find_name_from_code(code)
            if name:
                self.gamedb.save_name(token, name)
            return flask.jsonify(score="still being computed. Check scoreboard later.")
        room = Room([prog])
        runner = GameRunner(self.game)
        try:
            score = runner.run_for_avg_score(room, times=self.avg_game_count, func=self._avg_game_func)
            self.gamedb.save_avg_score(token, score)
            self.gamedb.save_code(token, code, options)
            name = find_name_from_code(code)
            if name:
                self.gamedb.save_name(token, name)
            return flask.jsonify(score=score)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            return flask.jsonify(
                error="Your bot ran into an error at runtime.\n"
                "If you think that your bot is correct, please file a bug report!\n"
                "Make sure to include your code."
            )

    @flask_classful.route("/sim", methods=["POST"])
    def sim(self):
        code = flask.request.get_json(silent=True).get("code", "")
        seed_str = flask.request.get_json(silent=True).get("seed", "")
        token = flask.request.get_json(silent=True).get("token", "").upper()
        opponents = flask.request.get_json(silent=True).get("opponents", None)
        options = flask.request.get_json(silent=True).get("options", None)
        if options is None:
            options = {}
        seed = random.randint(0, sys.maxsize)
        if seed_str:
            try:
                seed = int(seed_str, 36)
            except:
                return flask.jsonify(error="Invalid Seed")
        try:
            prog = self.compiler.compile(code)
            prog.options = options
            prog.token = ANONYMOUS_USER  # anonymous user
            prog.name = "Your bot"
        except:
            return flask.jsonify(error="Code did not compile")
        if self.gamedb.is_user_token(token):
            self.gamedb.save_code(token=token, code=code, options=options, set_as_active=False)
        room = Room(bots=[prog], seed=seed)
        if self.game.MULTIPLAYER:
            players = []
            if opponents is None:
                computer_bot_class = self.game.default_prog_for_computer()
                for _ in range(self.game.get_number_of_players() - 1):
                    players += [computer_bot_class()]
            else:
                for opponent in opponents:
                    if opponent == ANONYMOUS_USER:
                        opponent_prog = self.compiler.compile(code)
                        opponent_prog.options = options
                        opponent_prog.name = "Your other bot"
                        players += [opponent_prog]
                    else:
                        return flask.jsonify(error="Not implemented yet :(")

            room = Room(bots=[prog] + players, seed=seed)
        runner = GameRunner(self.game)
        try:
            gtoken = runner.run(room, playback=True).save(self.gamedb)
            result = ujson.dumps({"gtoken": gtoken})
        except Exception:
            traceback.print_exc(file=sys.stdout)
            return flask.jsonify(
                error="Your bot ran into an error at runtime.\n"
                "If you think that your bot is correct, please file a bug report!\n"
                "Make sure to include your code."
            )
        return result

    @flask_classful.route("/check_token", methods=["POST"])
    def check_token(self):
        token = flask.request.get_json(silent=True).get("token", "").upper()
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        else:
            return flask.jsonify(result=True)

    @flask_classful.route("/load_code", methods=["POST"])
    def load_code(self):
        token = flask.request.get_json(silent=True).get("token", "").upper()
        if not self.gamedb.is_user_token(token):
            return flask.jsonify(error="Invalid Token")
        else:
            code, options = self.gamedb.get_active_code_and_options(token)
            return flask.jsonify(code=code, options=options)

    @flask_classful.route("/play", methods=["POST"])
    def play(self):
        request = flask.request.get_json(silent=True)
        move = request.get("move", "")
        state = request.get("state", {})
        moves = state.get("moves", "")
        seed_str = state.get("seed", None)
        self.app.logger.debug(f"[move: {move}, state: {state}, moves: {moves}, seed: {seed_str}]")

        seed = random.randint(0, sys.maxsize)
        if seed_str:
            try:
                seed = int(seed_str, 36)
            except:
                return flask.jsonify(error="Invalid Seed")

        seed_str = int2base(seed, 36)
        hash_key = seed_str + moves

        if hash_key in self.play_game_cache:
            self.app.logger.debug("In cache")
            game_state = self.play_game_cache.pop(hash_key)
        else:
            self.app.logger.debug(f"Not in Cache. Hash Key: '{hash_key}'")
            game_state = GameRunner(self.game).init_game(seed=seed)
            for prev_move in moves:
                game_state = GameRunner.move_game(game_state, prev_move)
        if move:
            new_hash_key = hash_key + move
            game_state = GameRunner.move_game(game_state, move)
            self.play_game_cache[new_hash_key] = game_state
            self.app.logger.debug(f"Storing Cache. Hash Key: '{new_hash_key}'")

        state = {"seed": seed_str, "moves": game_state.moves}
        return flask.jsonify(frame=game_state.frame, state=state, lost=not game_state.game.is_running())

    def index(self):
        intro = self.game.get_intro() + GameLanguage.get_language_description(self.language)
        if self.game.GRID:
            return flask.render_template(
                "grid.html",
                game_title=self.game.GAME_TITLE,
                example_bot=self.game.default_prog_for_bot(self.language),
                char_width=self.game.CHAR_WIDTH,
                char_height=self.game.CHAR_HEIGHT,
                screen_width=self.game.SCREEN_WIDTH,
                screen_height=self.game.SCREEN_HEIGHT,
                char_set=self.charset,
                intro_text=intro,
                multiplayer=self.game.MULTIPLAYER,
            )
        else:
            return flask.render_template(
                "nongrid.html",
                game_title=self.game.GAME_TITLE,
                example_bot=self.game.default_prog_for_bot(self.language),
                screen_width=self.game.SCREEN_WIDTH,
                screen_height=self.game.SCREEN_HEIGHT,
                intro_text=intro,
                multiplayer=self.game.MULTIPLAYER,
                options=self.game.OPTIONS,
            )

    @classmethod
    def serve(
        cls,
        game,
        host="",
        port=5000,
        compression=False,
        language=GameLanguage.LITTLEPY,
        avg_game_count=10,
        multiplayer_scoring_interval=20,
        num_of_threads=None,
        game_data_path="temp_game",
        avg_game_func=average,
        debug=False,
        reuse_addr=None,
        play_cache_size=64,
        error_log_file="{dbfile}/log/error.log",
        debug_log_file="{dbfile}/log/debug.log",
    ):
        cls.game = game
        cls.host = host
        cls.port = port
        cls.compression = compression
        cls.language = language
        cls.avg_game_count = avg_game_count
        cls._avg_game_func = avg_game_func
        cls.gamedb = GameDB(game_data_path)
        cls.play_game_cache = LRUCache(play_cache_size)
        # setup anonymous school with an anonymous user
        if not cls.gamedb.is_school_token(ANONYMOUS_SCHOOL):
            cls.gamedb.add_new_school(_token=ANONYMOUS_SCHOOL)
        if not cls.gamedb.is_user_token(ANONYMOUS_USER):
            cls.gamedb.get_new_token(ANONYMOUS_SCHOOL, _token=ANONYMOUS_USER)
        if not cls.gamedb.is_comp_token(ANONYMOUS_COMP):
            cls.gamedb.add_new_competition(_token=ANONYMOUS_COMP)

        print("Building www cache...")
        cls.gamedb.www_cache.safe_replace_cache(os.path.join(os.path.split(__file__)[0], "www"))

        if issubclass(game, GridGame):
            cls.charset = cls.__copy_in_charset(game.CHAR_SET)

        setup_logging(
            debug_file=debug_log_file.replace("{dbfile}", game_data_path),
            error_file=error_log_file.replace("{dbfile}", game_data_path),
        )
        cls.app = flask.Flask(
            __name__.split(".")[0],
            static_url_path="",
            static_folder=cls.gamedb.www_cache.static_dir,
            template_folder=cls.gamedb.www_cache.template_dir,
            root_path=cls.gamedb.www_cache.root_dir,
        )
        cls.app.config["REQUEST_ID_UNIQUE_VALUE_PREFIX"] = "CYLGAME-"

        @cls.app.template_filter("markdown")
        def markdown_filter(data):
            from flask import Markup
            from markdown import markdown

            return Markup(markdown(data))

        if cls.compression:
            # BUUT WHAT ABOUT BREACH ATTACKS
            import flask_compress

            flask_compress.Compress(cls.app)

        RequestID(cls.app)
        cls.register(cls.app)
        cls.__load_language()

        @cls.app.errorhandler(500)
        def page_not_found(error):
            exception_str = "".join(traceback.TracebackException.from_exception(error.original_exception).format())
            token = cls.gamedb.save_exception(
                {
                    "exception": exception_str,
                    "url": flask.request.base_url,
                    "request": flask.request.get_json(silent=True),
                    "timestamp": datetime.utcnow().timestamp(),
                }
            )
            return f"Internal Server Exception. Exception Report {token}", 500

        print("Starting server at {}:{}".format(cls.host, cls.port))

        if cls.game.MULTIPLAYER and multiplayer_scoring_interval >= 0:
            if debug:
                print("Starting scoring process...")
            scoring_process = RollingMultiplayerCompRunner(
                multiplayer_scoring_interval, cls.gamedb, cls.game, cls.compiler, debug=debug
            )
            # scoring_process = MultiplayerCompRunner(multiplayer_scoring_interval, cls.gamedb, cls.game, cls.compiler, debug=debug)
            scoring_process.start()

        if debug:
            print("Debug Enabled.")
            cls.app.run(cls.host, cls.port)
        else:
            from gevent.pywsgi import WSGIServer
            from gevent.server import _tcp_listener

            listener = _tcp_listener((cls.host, cls.port), reuse_addr=reuse_addr)

            def serve_forever(listener):
                try:
                    WSGIServer(listener, cls.app).serve_forever()
                except KeyboardInterrupt:
                    pass

            if num_of_threads is None:
                num_of_threads = multiprocessing.cpu_count()

            for i in range(num_of_threads):
                Process(target=serve_forever, args=(listener,)).start()

            serve_forever(listener)

        print("Dying...")
        if cls.game.MULTIPLAYER:
            scoring_process.stop()
        print("All good :)")


# This is for backwards compatibility
serve = GameServer.serve
