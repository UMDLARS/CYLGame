import os
import ujson
import random


# TODO(derpferd): Use the move function to prevent RACE on files
class GameDB(object):
    TOKEN_LEN = 8

    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.data_dir = os.path.join(self.game_dir, "data")
        self.schools_dir = os.path.join(self.game_dir, "schools")
        self.__load()

    def __load(self):
        # is_new = False
        if not os.path.exists(self.game_dir):
            # is_new = True
            os.mkdir(self.game_dir)
        if not os.path.exists(self.data_dir):
            # is_new = True
            os.mkdir(self.data_dir)
        if not os.path.exists(self.schools_dir):
            # is_new = True
            os.mkdir(self.schools_dir)

        # if is_new:
        #
        #     # self.schools = {}
        #     # self.tokens = {}
        #     # self.__save()
        # else:
        #     obj = ujson.load(open(self.meta_fn, "r"))
        #     assert "schools" in obj
        #     assert "tokens" in obj
        #     self.schools = obj["schools"]
        #     self.tokens = obj["tokens"]

    # def __save(self):
    #     ujson.dump({"schools": self.schools, "tokens": self.tokens}, open(self.meta_fn, "w"))

    def __get_user_tokens(self):
        return os.listdir(self.data_dir)

    def __get_school_tokens(self):
        return os.listdir(self.schools_dir)

    def __get_school_user_tokens(self, school_tk):
        if self.is_school_token(school_tk):
            return os.listdir(self.__get_dir_for_token(school_tk, "tokens"))
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
        elif self.is_school_token(token):
            return os.path.join(self.schools_dir, token, *fns)
        return None

    def is_school_token(self, token):
        if len(token) > 0 and token[0] == "S":
            # It is a school token
            return token in self.__get_school_tokens()
        return False

    def is_user_token(self, token):
        return token in self.__get_user_tokens()

    def get_new_token(self, school_tk):
        # Is name needed?
        assert self.is_school_token(school_tk)
        token = self.__get_new_token()

        # Touch the file
        with open(self.__get_dir_for_token(school_tk, ["tokens", token]), "w") as fp:
            pass

        # Create token dir
        os.mkdir(os.path.join(self.data_dir, token))
        return token

    def add_new_school(self, name=""):
        token = self.__get_new_token(self.__get_school_tokens(), prefix="S")

        os.mkdir(self.__get_dir_for_token(token))
        os.mkdir(self.__get_dir_for_token(token, "tokens"))

        with open(self.__get_dir_for_token(token, "name")) as fp:
            fp.write(name)

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

    def save_name(self, token, name):
        """Save a user's name under their token.

        Args:
            token (str): The user's token.
            name (str): The user's name.
        """
        assert os.path.exists(self.__get_dir_for_token(token))
        with open(self.__get_dir_for_token(token, "name"), "w") as fp:
            fp.write(name)

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

    def get_name(self, token):
        if self.is_user_token(token):
            if os.path.exists(self.__get_dir_for_token(token, "name")):
                with open(self.__get_dir_for_token(token, "name"), "r") as fp:
                    return fp.read()
        elif self.is_school_token(token):
            if os.path.exists(self.__get_dir_for_token(token, "name")):
                with open(self.__get_dir_for_token(token, "name"), "r") as fp:
                    return fp.read()
        return None

    def get_avg_score(self, token):
        if os.path.exists(self.__get_dir_for_token(token, "avg_score")):
            with open(self.__get_dir_for_token(token, "avg_score"), "r") as fp:
                return int(fp.read())
        else:
            return None

    # def get_name(self, token):
    #     if self.is_user_token(token):
    #         return self.
    #         return self.tokens[token]["name"]
    #     elif self.is_school_token(token):
    #         return self.schools[token]["name"]

    def get_school_for_token(self, token):
        for school in self.__get_school_tokens():
            if token in self.__get_school_user_tokens(school):
                return school
        return None

    def get_tokens_for_school(self, school_tk):
        return self.__get_school_user_tokens(school_tk)

    def get_school_tokens(self):
        return self.__get_school_tokens()
