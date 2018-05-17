import gzip
import io
import os
import shutil
import random
import time
import msgpack
from builtins import str as text


def write_json(o, filename):
    with gzip.open(filename, "w") as fp:
        msgpack.dump(o, fp, encoding='utf-8')


def read_json(filename):
    with gzip.open(filename, "r") as fp:
        return msgpack.load(fp, encoding='utf-8')


class WWWCache:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def safe_replace_cache(self, www_dir):
        """This function safely replaces the current www cached data with the data found in `www_dir`
        """
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
    TOKEN_LEN = 8

    def __init__(self, root_dir):
        self.root_dir = os.path.abspath(root_dir)
        self.data_dir = os.path.join(self.root_dir, "data")
        self.game_dir = os.path.join(self.root_dir, "games")
        self.schools_dir = os.path.join(self.root_dir, "schools")
        self.competitions_dir = os.path.join(self.root_dir, "competitions")
        self.www_cache = WWWCache(os.path.join(self.root_dir, "www"))
        self.__load()

    def __load(self):
        if not os.path.exists(self.root_dir):
            os.mkdir(self.root_dir)
        if not os.path.exists(self.game_dir):
            os.mkdir(self.game_dir)
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)
        if not os.path.exists(self.schools_dir):
            os.mkdir(self.schools_dir)
        if not os.path.exists(self.competitions_dir):
            os.mkdir(self.competitions_dir)

    def __get_user_tokens(self):
        return os.listdir(self.data_dir)

    def __get_game_tokens(self):
        return os.listdir(self.game_dir)

    def __get_school_tokens(self):
        return os.listdir(self.schools_dir)

    def __get_comp_tokens(self):
        return os.listdir(self.competitions_dir)

    def __get_school_user_tokens(self, school_tk):
        if self.is_school_token(school_tk):
            return os.listdir(self.__get_dir_for_token(school_tk, "tokens"))
        return []

    def __get_user_game_tokens(self, token):
        if self.is_user_token(token):
            return os.listdir(self.__get_dir_for_token(token, "games"))
        return []

    def __get_comp_game_tokens(self, token):
        if self.is_comp_token(token):
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

    def __get_dir_for_token(self, token, fns=[]):
        """Get the file path for a given token and optionally an additional path after the token dir.

        Args:
            token (str): The user's token.
            fns (str or list): The file or files to add after the token directory.
        """
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
        os.mkdir(os.path.join(self.data_dir, token))
        os.mkdir(os.path.join(self.data_dir, token, "games"))
        return token

    def add_new_school(self, name="", _token=None):  # Don't use `_token` unless you know what you are doing.
        token = _token
        if _token is None:
            token = self.__get_new_token(self.__get_school_tokens(), prefix="S")

        os.mkdir(os.path.join(self.schools_dir, token))
        os.mkdir(os.path.join(self.schools_dir, token, "tokens"))

        with io.open(os.path.join(self.schools_dir, token, "name"), "w", encoding="utf8") as fp:
            fp.write(text(name))

        return token

    def add_new_competition(self, name="", _token=None):
        token = _token
        if token is None:
            token = self.__get_new_token(self.__get_comp_tokens(), prefix="P")

        os.mkdir(os.path.join(self.competitions_dir, token))
        os.mkdir(os.path.join(self.competitions_dir, token, "schools"))
        os.mkdir(os.path.join(self.competitions_dir, token, "games"))

        with io.open(os.path.join(self.competitions_dir, token, "name"), "w", encoding="utf8") as fp:
            fp.write(text(name))

        return token

    def add_new_game(self, frames=None, per_player_data=None, player_tokens=None):
        if per_player_data is not None:
            assert player_tokens is None
        if player_tokens is not None:
            assert per_player_data is None

        token = self.__get_new_token(self.__get_game_tokens(), prefix="G")

        os.mkdir(os.path.join(self.game_dir, token))
        os.mkdir(os.path.join(self.game_dir, token, "players"))

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
        if not os.path.exists(school_dir):
            os.mkdir(school_dir)

    # TODO(derpferd): add function to remove a school

    def set_comp_school_code(self, ctoken, stoken, code):
        assert self.is_comp_token(ctoken)
        assert self.is_school_token(stoken)

        school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
        if not os.path.exists(school_dir):
            os.mkdir(school_dir)

        with io.open(os.path.join(school_dir, "code.lp"), "w", encoding="utf8") as fp:
            fp.write(text(code))

    # def set_token_for_comp(self, ctoken, utoken, stoken):
    #     assert self.is_comp_token(ctoken)
    #     assert self.is_user_token(utoken)
    #     assert self.is_school_token(stoken)
    #
    #     school_dir = self.__get_dir_for_token(ctoken, ["schools", stoken])
    #     if not os.path.exists(school_dir):
    #         os.mkdir(school_dir)
    #     with io.open(os.path.join(school_dir, "code.lp"), "w", encoding="utf8") as fp:
    #         code = self.get_code(utoken)
    #         assert code is not None
    #         fp.write(code)
    #     # with open(os.path.join(school_dir, "name"), "w") as fp:
    #     #     name = self.get_name(stoken)
    #     #     assert name is not None
    #     #     fp.write(name)

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

    def save_code(self, token, code, options=None):
        """Save a user's code under their token.

        Args:
            token (str): The user's token.
            code (str): The user's code.
            options (json-able object): The user's options.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        with io.open(self.__get_dir_for_token(token, "code.lp"), "w", encoding="utf8") as fp:
            fp.write(text(code))
        if options:
            write_json(options, self.__get_dir_for_token(token, "options.mp.gz"))

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

    def save_game_frames(self, gtoken, frames):
        assert os.path.exists(self.__get_dir_for_token(gtoken))
        write_json(frames, self.__get_dir_for_token(gtoken, "frames.mp.gz"))

    def set_game_player(self, gtoken, token, data=None):
        assert os.path.exists(self.__get_dir_for_token(gtoken, "players"))
        assert self.is_user_token(token), "Token '{}' must be a user token".format(token)
        if not os.path.exists(self.__get_dir_for_token(token, "games")):
            os.mkdir(self.__get_dir_for_token(token, "games"))
        assert os.path.exists(self.__get_dir_for_token(token, "games")), "Player token must have a games directory."

        os.mkdir(self.__get_dir_for_token(gtoken, ["players", token]))

        write_json(data, self.__get_dir_for_token(gtoken, ["players", token, "data.mp.gz"]))

        with open(self.__get_dir_for_token(token, ["games", gtoken]), "w"):
            pass

    def add_game_to_comp(self, ctoken, gtoken):
        with open(self.__get_dir_for_token(ctoken, ["games", gtoken]), "w"):
            pass

    def remove_game_from_comp(self, ctoken, gtoken):
        os.remove(self.__get_dir_for_token(ctoken, ["games", gtoken]))

    def replace_games_in_comp(self, ctoken, new_gtokens, cleanup=True):
        os.mkdir(os.path.join(self.competitions_dir, ctoken, "new_games"))
        for gtoken in new_gtokens:
            with open(self.__get_dir_for_token(ctoken, ["new_games", gtoken]), "w"):
                pass

        cleanup_gtokens = []
        if cleanup:
            cleanup_gtokens = self.__get_comp_game_tokens(ctoken)

        has_old_games = os.path.exists(os.path.join(self.competitions_dir, ctoken, "games"))
        if has_old_games:
            os.rename(os.path.join(self.competitions_dir, ctoken, "games"),
                      os.path.join(self.competitions_dir, ctoken, "old_games"))
        os.rename(os.path.join(self.competitions_dir, ctoken, "new_games"),
                  os.path.join(self.competitions_dir, ctoken, "games"))
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

    def get_code_and_options(self, token):
        code, options = None, {}
        if os.path.exists(self.__get_dir_for_token(token, "code.lp")):
            with io.open(self.__get_dir_for_token(token, "code.lp"), "r", encoding="utf8") as fp:
                code = fp.read()
        if os.path.exists(self.__get_dir_for_token(token, "options.mp.gz")):
            options = read_json(self.__get_dir_for_token(token, "options.mp.gz"))
        return code, options

    def get_name(self, token):
        if self.is_user_token(token) or self.is_school_token(token) or self.is_comp_token(token):
            if os.path.exists(self.__get_dir_for_token(token, "name")):
                with io.open(self.__get_dir_for_token(token, "name"), "r", encoding="utf8") as fp:
                    return fp.read()
        return None

    def get_avg_score(self, token):
        if os.path.exists(self.__get_dir_for_token(token, "avg_score")):
            with io.open(self.__get_dir_for_token(token, "avg_score"), "r", encoding="utf8") as fp:
                try:
                    # Try to convert to float
                    return float(fp.read())
                except ValueError as e:
                    # If failed return none
                    return None
        else:
            return None

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

    def delete_game(self, gtoken):
        # TODO: add a test for this method
        assert self.is_game_token(gtoken)
        for player in self.get_players_for_game(gtoken):
            os.remove(self.__get_dir_for_token(player, ["games", gtoken]))
        shutil.rmtree(self.__get_dir_for_token(gtoken))
