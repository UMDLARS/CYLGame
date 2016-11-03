import os
import ujson
import random


# TODO(derpferd): make thread safe in future.
class GameDB(object):
    TOKEN_LEN = 8

    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.data_dir = os.path.join(self.game_dir, "data")
        self.meta_fn = os.path.join(self.game_dir, "metadata.json")
        self.__load()

    def __load(self):
        is_new = False
        if not os.path.exists(self.game_dir):
            is_new = True
            os.mkdir(self.game_dir)
        if not os.path.exists(self.data_dir):
            is_new = True
            os.mkdir(self.data_dir)
        if not os.path.exists(self.meta_fn):
            is_new = True

        if is_new:
            self.schools = {}
            self.tokens = {}
            self.__save()
        else:
            obj = ujson.load(open(self.meta_fn, "r"))
            assert "schools" in obj
            assert "tokens" in obj
            self.schools = obj["schools"]
            self.tokens = obj["tokens"]

    def __save(self):
        ujson.dump({"schools": self.schools, "tokens": self.tokens}, open(self.meta_fn, "w"))

    def __get_new_token(self, tokens=None, prefix=""):

        def new_token():
            return prefix + "".join([random.choice("0123456789ABCDEF") for _ in range(self.TOKEN_LEN)])
        if not tokens:
            tokens = self.tokens
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
        return os.path.join(self.data_dir, token, *fns)

    def is_school_token(self, token):
        if len(token) > 0 and token[0] == "S":
            # It is a school token
            return token in self.schools
        return False

    def is_user_token(self, token):
        return token in self.tokens

    def get_new_token(self, school_tk, name=""):
        # Is name needed?
        assert school_tk in self.schools
        token = self.__get_new_token()
        self.schools[school_tk]["tokens"] += [token]
        self.tokens[token] = {"name": name}
        os.mkdir(self.__get_dir_for_token(token))
        self.__save()
        return token

    def add_new_school(self, name=""):
        token = self.__get_new_token(self.schools.keys(), prefix="S")
        self.schools[token] = {"name": name, "tokens": []}
        self.__save()
        return token

    def save_code(self, token, code):
        """Save a user's code under their token.

        Args:
            token (str): The user's token.
            code (str): The user's code.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        with open(self.__get_dir_for_token(token, "code.lp"), "w") as fp:
            fp.write(code)

    def save_avg_score(self, token, score):
        """Save a user's average score.

        Args:
            token (str): The user's token.
            score (int): The user's average score.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        with open(self.__get_dir_for_token(token, "avg_score"), "w") as fp:
            fp.write(str(score))

    def get_code(self, token):
        if os.path.exists(self.__get_dir_for_token(token, "code.lp")):
            with open(self.__get_dir_for_token(token, "code.lp"), "r") as fp:
                return fp.read()
        else:
            return None

    def get_avg_score(self, token):
        if os.path.exists(self.__get_dir_for_token(token, "avg_score")):
            with open(self.__get_dir_for_token(token, "avg_score"), "r") as fp:
                return int(fp.read())
        else:
            return None

    def get_name(self, token):
        if self.is_user_token(token):
            return self.tokens[token]["name"]
        elif self.is_school_token(token):
            return self.schools[token]["name"]

    def get_school_for_token(self, token):
        for school in self.schools:
            if token in self.schools[school]["tokens"]:
                return school
        return None

    def get_tokens_for_school(self, school_tk):
        return self.schools[school_tk]["tokens"]
