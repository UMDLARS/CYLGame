import gzip
import io
import os
import random
import shutil
import time
from builtins import str as text

import msgpack

from CYLGame.Utils import hash_stream


def write_json(o, filename):
    with gzip.open(filename, "w") as fp:
        msgpack.dump(o, fp)


def read_json(filename):
    with gzip.open(filename, "r") as fp:
        return msgpack.load(fp)


class WWWCache:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def safe_replace_cache(self, www_dir):
        """This function safely replaces the current www cached data with the data found in `www_dir`"""
        if not os.path.exists(self.root_dir):
            # no old cache
            shutil.copytree(www_dir, self.root_dir)
        else:
            tmp_dir = os.path.join(self.root_dir + "_tmp")
            old_dir = os.path.join(self.root_dir + "_old")

            # make sure the tmp dir doesn't already exist
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

            # make sure the old dir doesn't already exist
            if os.path.exists(old_dir):
                shutil.rmtree(old_dir)

            # copy in the new data
            shutil.copytree(www_dir, tmp_dir)

            # move old cache dir
            os.rename(self.root_dir, old_dir)

            # move in new cache dir
            try:
                os.rename(tmp_dir, self.root_dir)
            except:
                # This is bad!!! The old cache is gone but the new can't be put in.
                # Try to put back old
                os.rename(old_dir, self.root_dir)
                raise

            # All good now clean up.
            shutil.rmtree(old_dir)

    @property
    def static_dir(self):
        return os.path.join(self.root_dir, "static")

    @property
    def template_dir(self):
        return os.path.join(self.root_dir, "templates")


# TODO(derpferd): Use the move function to prevent RACE on files
class GameDB(object):
    """
    This is the database that stores all persisted data. This database is a file based DB.

    /                           => Root game directory
    /data                       => Should be named something like "users". This stores user related data.
    /data/TOKEN                 => A directory containing data for the user with the token TOKEN.
    /data/TOKEN/avg_score       => File containing a single float representing the average score for the user.
    /data/TOKEN/name            => File containing the name for the user.
    /data/TOKEN/code            => Directory containing all code submitted by the user.
    /data/TOKEN/code/CTIME_HASH => The code submitted or played at CTIME.
    /data/TOKEN/code/CTIME_HASH/code.lp
    /data/TOKEN/code/CTIME_HASH/options.mp.gz
    /data/TOKEN/games           => A directory related games.
    /data/TOKEN/games/GTOKEN    => An empty file representing that the users bot was used in game GTOKEN.
    /games                      => Stores game related data.
    /schools                    => Stores school related data.
    /competitions               => Stores competition related data.
    /www                        => Stores static and template files for the server. This is a cache that is deleted and
                                    recreated on each restart.
    """

    TOKEN_LEN = 8

    ACTIVE_CODE_KEY = "active_code"

    CODE_DIR = "code"
    CODE_FILENAME = "code.lp"
    OPTIONS_FILENAME = "options.mp.gz"

    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.data_dir = os.path.join(self.root_dir, "data")
        self.game_dir = os.path.join(self.root_dir, "games")
        self.schools_dir = os.path.join(self.root_dir, "schools")
        self.competitions_dir = os.path.join(self.root_dir, "competitions")
        self.exception_dir = os.path.join(self.root_dir, "exceptions")
        self.www_cache = WWWCache(os.path.join(self.root_dir, "www"))
        self.__load()

    def __load(self):
        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.game_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.schools_dir, exist_ok=True)
        os.makedirs(self.competitions_dir, exist_ok=True)
        os.makedirs(self.exception_dir, exist_ok=True)

    def __get_user_tokens(self):
        return os.listdir(self.data_dir)

    def __get_game_tokens(self):
        return os.listdir(self.game_dir)

    def __get_school_tokens(self):
        return os.listdir(self.schools_dir)

    def __get_comp_tokens(self):
        return os.listdir(self.competitions_dir)

    def __get_exception_tokens(self):
        return os.listdir(self.exception_dir)

    def __get_school_user_tokens(self, school_tk):
        if self.is_school_token(school_tk):
            return os.listdir(self.__get_dir_for_token(school_tk, "tokens"))
        return []

    def __get_user_game_tokens(self, token):
        if self.is_user_token(token) and os.path.exists(self.__get_dir_for_token(token, "games")):
            return os.listdir(self.__get_dir_for_token(token, "games"))
        return []

    def __get_comp_game_tokens(self, token):
        if self.is_comp_token(token) and os.path.exists(self.__get_dir_for_token(token, "games")):
            return os.listdir(self.__get_dir_for_token(token, "games"))
        return []

    def __get_new_token(self, tokens=None, prefix=""):
        def new_token():
            return prefix + "".join([random.choice("0123456789ABCDEF") for _ in range(self.TOKEN_LEN)])

        if not tokens:
            tokens = self.__get_user_tokens()
        token = new_token()
        while token in tokens:
            token = new_token()
        return token

    def __get_dir_for_token(self, token, fns=None):
        """Get the file path for a given token and optionally an additional path after the token dir.

        Args:
            token (str): The user's token.
            fns (str or list): The file or files to add after the token directory.
        """
        if fns is None:
            fns = list()
        if isinstance(fns, str):
            fns = [fns]
        else:
            assert isinstance(fns, list)
        if self.is_user_token(token):
            return os.path.join(self.data_dir, token, *fns)
        elif self.is_game_token(token):
            return os.path.join(self.game_dir, token, *fns)
        elif self.is_school_token(token):
            return os.path.join(self.schools_dir, token, *fns)
        elif self.is_comp_token(token):
            return os.path.join(self.competitions_dir, token, *fns)
        elif self.is_exception_token(token):
            return os.path.join(self.exception_dir, token, *fns)
        return None

    def __get_cur_code_for_token(self, token):
        pass

    def __get_next_code_for_token(self, token):
        pass

    def is_comp_token(self, token):
        if len(token) > 0 and token[0] == "P":
            # It is a competition token
            return token in self.__get_comp_tokens()
        return False

    def is_school_token(self, token):
        if len(token) > 0 and token[0] == "S":
            # It is a school token
            return token in self.__get_school_tokens()
        return False

    def is_user_token(self, token):
        return token in self.__get_user_tokens()

    def is_game_token(self, gtoken):
        gtks = self.__get_game_tokens()
        return gtoken in gtks

    def is_exception_token(self, token):
        if len(token) > 0 and token[0] == "E":
            return token in self.__get_exception_tokens()
        return False

    def get_new_token(self, school_tk, _token=None):  # Don't use `_token` unless you know what you are doing.
        # Is name needed?
        assert self.is_school_token(school_tk)
        token = _token
        if _token is None:
            token = self.__get_new_token()

        # Touch the file
        with open(self.__get_dir_for_token(school_tk, ["tokens", token]), "w") as fp:
            pass

        # Create token dir
        os.makedirs(os.path.join(self.data_dir, token))
        os.makedirs(os.path.join(self.data_dir, token, "games"))
        return token

    def add_new_school(self, name="", _token=None):  # Don't use `_token` unless you know what you are doing.
        token = _token
        if _token is None:
            token = self.__get_new_token(self.__get_school_tokens(), prefix="S")

        os.makedirs(os.path.join(self.schools_dir, token))
        os.makedirs(os.path.join(self.schools_dir, token, "tokens"))

        with io.open(os.path.join(self.schools_dir, token, "name"), "w", encoding="utf8") as fp:
            fp.write(text(name))

        return token

    def add_new_competition(self, name="", _token=None):
        token = _token
        if token is None:
            token = self.__get_new_token(self.__get_comp_tokens(), prefix="P")

        os.makedirs(os.path.join(self.competitions_dir, token))
        os.makedirs(os.path.join(self.competitions_dir, token, "schools"))
        os.makedirs(os.path.join(self.competitions_dir, token, "games"))

        with io.open(os.path.join(self.competitions_dir, token, "name"), "w", encoding="utf8") as fp:
            fp.write(text(name))

        return token

    def add_new_game(self, frames=None, per_player_data=None, player_tokens=None):
        if per_player_data is not None:
            assert player_tokens is None
        if player_tokens is not None:
            assert per_player_data is None

        token = self.__get_new_token(self.__get_game_tokens(), prefix="G")

        os.makedirs(os.path.join(self.game_dir, token))
        os.makedirs(os.path.join(self.game_dir, token, "players"))

        if frames is not None:
            self.save_game_frames(token, frames)

        if player_tokens is not None:
            for player in player_tokens:
                self.set_game_player(token, player)
        elif per_player_data is not None:
            for player, data in per_player_data.items():
                self.set_game_player(token, player, data)

        with open(os.path.join(self.game_dir, token, "ctime"), "w") as fp:
            fp.write(text(time.time()))

        return token

    def add_school_to_comp(self, ctoken, stoken):
        assert self.is_comp_token(ctoken)
        assert self.is_school_token(stoken)

        school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
        os.makedirs(school_dir, exist_ok=True)

    # TODO(derpferd): add function to remove a school

    def set_comp_school_code(self, ctoken, stoken, code):
        assert self.is_comp_token(ctoken)
        assert self.is_school_token(stoken)

        school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
        os.makedirs(school_dir, exist_ok=True)

        with io.open(os.path.join(school_dir, "code.lp"), "w", encoding="utf8") as fp:
            fp.write(text(code))

    # def set_token_for_comp(self, ctoken, utoken, stoken):
    #     assert self.is_comp_token(ctoken)
    #     assert self.is_user_token(utoken)
    #     assert self.is_school_token(stoken)
    #
    #     school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
    #     if not os.path.exists(school_dir):
    #         os.makedirs(school_dir)
    #     with io.open(os.path.join(school_dir, "code.lp"), "w", encoding="utf8") as fp:
    #         code = self.get_code(utoken)
    #         assert code is not None
    #         fp.write(code)
    #     # with open(os.path.join(school_dir, "name"), "w") as fp:
    #     #     name = self.get_name(stoken)
    #     #     assert name is not None
    #     #     fp.write(name)

    def get_ctime_for_game(self, token):
        with open(os.path.join(self.game_dir, token, "ctime"), "r") as fp:
            return float(fp.read())

    def get_comp_code(self, ctoken, stoken):
        school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
        if os.path.exists(os.path.join(school_dir, "code.lp")):
            with io.open(os.path.join(school_dir, "code.lp"), "r", encoding="utf8") as fp:
                return fp.read()
        else:
            return None

    def get_comp_tokens(self):
        return self.__get_comp_tokens()

    def get_comps_for_token(self, utoken):
        comps = []
        stoken = self.get_school_for_token(utoken)
        for comp in self.__get_comp_tokens():
            if stoken in self.get_schools_in_comp(comp):
                comps += [comp]
        return comps

    def get_schools_in_comp(self, ctoken):
        return os.listdir(self.__get_dir_for_token(ctoken, "schools"))

    def set_comp_avg_score(self, ctoken, stoken, score):
        school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
        assert school_dir is not None
        with io.open(os.path.join(school_dir, "avg_score"), "w", encoding="utf8") as fp:
            fp.write(text(score))

    def get_comp_avg_score(self, ctoken, stoken):
        school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
        if os.path.exists(os.path.join(school_dir, "avg_score")):
            with io.open(os.path.join(school_dir, "avg_score"), "r", encoding="utf8") as fp:
                return float(fp.read())
        else:
            return None

    def save_code(self, token, code, options=None, set_as_active=True):
        """Save a user's code under their token.

        Args:
            token (str): The user's token.
            code (str): The user's code.
            options (json-able object): The user's options.
            set_as_active (bool): Whether to set the saved code as the active code for the token.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        code_dir = self.__get_dir_for_token(token, self.CODE_DIR)
        os.makedirs(code_dir, exist_ok=True)

        # Create Code id.
        ctime = int(time.time_ns())
        buf = io.BytesIO()
        buf.write(bytes(code, encoding="utf8"))
        if options:
            msgpack.dump(options, buf)
        buf.seek(0)
        code_hash = hash_stream(buf)
        code_path_name = f"{ctime}_{code_hash}"
        try:
            os.makedirs(os.path.join(code_dir, code_path_name))
        except OSError:
            raise ValueError("Duplicate Request!")

        # Write code
        with io.open(os.path.join(code_dir, code_path_name, self.CODE_FILENAME), "w", encoding="utf8") as fp:
            fp.write(text(code))
        if options:
            write_json(options, os.path.join(code_dir, code_path_name, self.OPTIONS_FILENAME))

        # Update code to be active if needed
        if set_as_active:
            self.save_value(token=token, key=self.ACTIVE_CODE_KEY, value=code_path_name)

    def save_name(self, token, name):
        """Save a user's name under their token.

        Args:
            token (str): The user's token.
            name (str): The user's name.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        with io.open(self.__get_dir_for_token(token, "name"), "w", encoding="utf8") as fp:
            fp.write(text(name))

    def save_avg_score(self, token, score):
        """Save a user's average score.

        Args:
            token (str): The user's token.
            score (int): The user's average score.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        with io.open(self.__get_dir_for_token(token, "avg_score"), "w", encoding="utf8") as fp:
            fp.write(text(score))

    def save_value(self, token, key, value):
        """Save a key value pair to a tokens directory. If a value has been saved under the same key it will be
            overwritten by the new value passed in. The value can be looked up using the `get_value` function.

        Args:
            token (str):    Any valid token.
            key (str):      The key to store the `value` under.
            value (str or int or float):    The value to be stored.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        assert isinstance(key, str) and (isinstance(value, str) or isinstance(value, int) or isinstance(value, float))

        obj = {}
        if os.path.exists(self.__get_dir_for_token(token, "db.mp.gz")):
            obj = read_json(self.__get_dir_for_token(token, "db.mp.gz"))
        obj[key] = value

        # We write all the data to a new file then move it to replace the old file to insure that the file is never half written.
        write_json(obj, self.__get_dir_for_token(token, "db.mp.gz.new"))
        os.rename(self.__get_dir_for_token(token, "db.mp.gz.new"), self.__get_dir_for_token(token, "db.mp.gz"))

    def get_value(self, token, key, default_value=None):
        if os.path.exists(self.__get_dir_for_token(token, "db.mp.gz")):
            return read_json(self.__get_dir_for_token(token, "db.mp.gz")).get(key, default_value)
        return default_value

    def save_game_frames(self, gtoken, frames):
        assert os.path.exists(self.__get_dir_for_token(gtoken))
        write_json(frames, self.__get_dir_for_token(gtoken, "frames.mp.gz"))

    def set_game_player(self, gtoken, token, data=None):
        assert os.path.exists(self.__get_dir_for_token(gtoken, "players"))
        assert self.is_user_token(token), "Token '{}' must be a user token".format(token)
        os.makedirs(self.__get_dir_for_token(token, "games"), exist_ok=True)
        assert os.path.exists(self.__get_dir_for_token(token, "games")), "Player token must have a games directory."

        os.makedirs(self.__get_dir_for_token(gtoken, ["players", token]))

        write_json(data, self.__get_dir_for_token(gtoken, ["players", token, "data.mp.gz"]))

        with open(self.__get_dir_for_token(token, ["games", gtoken]), "w"):
            pass

    def add_game_to_comp(self, ctoken, gtoken):
        with open(self.__get_dir_for_token(ctoken, ["games", gtoken]), "w"):
            pass

    def remove_game_from_comp(self, ctoken, gtoken):
        os.remove(self.__get_dir_for_token(ctoken, ["games", gtoken]))

    def replace_games_in_comp(self, ctoken, new_gtokens, cleanup=True):
        os.makedirs(os.path.join(self.competitions_dir, ctoken, "new_games"))
        for gtoken in new_gtokens:
            with open(self.__get_dir_for_token(ctoken, ["new_games", gtoken]), "w"):
                pass

        cleanup_gtokens = []
        if cleanup:
            cleanup_gtokens = self.__get_comp_game_tokens(ctoken)

        has_old_games = os.path.exists(os.path.join(self.competitions_dir, ctoken, "games"))
        if has_old_games:
            os.rename(
                os.path.join(self.competitions_dir, ctoken, "games"),
                os.path.join(self.competitions_dir, ctoken, "old_games"),
            )
        os.rename(
            os.path.join(self.competitions_dir, ctoken, "new_games"),
            os.path.join(self.competitions_dir, ctoken, "games"),
        )
        shutil.rmtree(os.path.join(self.competitions_dir, ctoken, "old_games"))

        for gtoken in cleanup_gtokens:
            self.delete_game(gtoken)

    def get_game_frames(self, gtoken):
        if os.path.exists(self.__get_dir_for_token(gtoken, "frames.mp.gz")):
            return read_json(self.__get_dir_for_token(gtoken, "frames.mp.gz"))

    def get_player_game_data(self, gtoken, token):
        if os.path.exists(self.__get_dir_for_token(gtoken, ["players", token, "data.mp.gz"])):
            return read_json(self.__get_dir_for_token(gtoken, ["players", token, "data.mp.gz"]))

    def get_games_for_token(self, token):
        if self.is_user_token(token):
            return self.__get_user_game_tokens(token)
        elif self.is_comp_token(token):
            return self.__get_comp_game_tokens(token)
        raise ValueError("Invalid token")

    def get_active_code_and_options(self, token):
        code, options = None, {}
        code_hash = self.get_value(token=token, key=self.ACTIVE_CODE_KEY)
        should_save_code = False
        if code_hash:
            base_path = self.__get_dir_for_token(token, [self.CODE_DIR, code_hash])
        else:
            base_path = self.__get_dir_for_token(token)
            should_save_code = True  # The code is stored in an older style. Upgrade it to the new style.

        code_path = os.path.join(base_path, self.CODE_FILENAME)
        options_path = os.path.join(base_path, self.OPTIONS_FILENAME)
        if os.path.exists(code_path):
            with io.open(code_path, "r", encoding="utf8") as fp:
                code = fp.read()
        if os.path.exists(options_path):
            options = read_json(options_path)
        if should_save_code and (code or options):
            self.save_code(token, code, options)
        return code, options

    def get_name(self, token):
        if self.is_user_token(token) or self.is_school_token(token) or self.is_comp_token(token):
            if os.path.exists(self.__get_dir_for_token(token, "name")):
                with io.open(self.__get_dir_for_token(token, "name"), "r", encoding="utf8") as fp:
                    return fp.read()
        return None

    def get_avg_score(self, token, default_value=None):
        if os.path.exists(self.__get_dir_for_token(token, "avg_score")):
            with io.open(self.__get_dir_for_token(token, "avg_score"), "r", encoding="utf8") as fp:
                try:
                    # Try to convert to float
                    return float(fp.read())
                except ValueError as e:
                    # If failed return none
                    return default_value
        else:
            return default_value

    def get_school_for_token(self, token):
        for school in self.__get_school_tokens():
            if token in self.__get_school_user_tokens(school):
                return school
        return None

    # Get tokens that belong to a school
    def get_tokens_for_school(self, school_tk):
        return self.__get_school_user_tokens(school_tk)

    def get_school_tokens(self):
        return self.__get_school_tokens()

    def get_players_for_game(self, gtoken):
        # TODO: add a test for this method
        return os.listdir(self.__get_dir_for_token(gtoken, "players"))

    def get_all_game_tokens(self):
        return self.__get_game_tokens()

    def get_all_comp_tokens(self):
        return self.__get_comp_tokens()

    def get_exception_tokens(self):
        return self.__get_exception_tokens()

    def delete_game(self, gtoken):
        # TODO: add a test for this method
        assert self.is_game_token(gtoken)
        for player in self.get_players_for_game(gtoken):
            os.remove(self.__get_dir_for_token(player, ["games", gtoken]))
        if gtoken in self.get_games_for_token("P00000000"):  # TODO: remove game from all comps where it is used.
            self.remove_game_from_comp("P00000000", gtoken)
        shutil.rmtree(self.__get_dir_for_token(gtoken))

    def save_exception(self, exception_report):
        token = self.__get_new_token(self.__get_exception_tokens(), prefix="E")

        os.makedirs(os.path.join(self.exception_dir, token))

        p = self.__get_dir_for_token(token, "report.mp.gz")
        write_json(exception_report, p)

        return token

    def get_exception(self, token):
        assert self.is_exception_token(token)
        self.__get_dir_for_token(token)

        if os.path.exists(self.__get_dir_for_token(token, "report.mp.gz")):
            return read_json(self.__get_dir_for_token(token, "report.mp.gz"))
