from __future__ import print_function
from __future__ import division

from itertools import islice
from random import random, choice, shuffle

from multiprocessing import Process, Event

import time

import math
from typing import Dict

from CYLGame.Utils import OnlineMean
from .Game import GameRunner
from .Player import Room


def create_room(gamedb, bot, compiler, size):
    stokens = gamedb.get_school_tokens()
    pool = []
    for stoken in stokens:
        pool += gamedb.get_tokens_for_school(stoken)

    if len(pool) == 0:
        from copy import deepcopy
        return Room([bot] + [deepcopy(bot) for _ in range(size - 1)])

    bots = [bot]
    while True:
        token = choice(pool)
        code, options = gamedb.get_code_and_options(token)
        try:
            prog = compiler.compile(code)
            prog.options = options
            bots += [prog]
            if len(bots) >= size:
                return Room(bots)
        except:
            print("Couldn't compile code for '{}' in '{}'".format(token, gamedb.get_school_for_token(token)))


def avg(scores):
    return float((sum(scores) * 100) / len(scores)) / 100


# TODO: rewrite this function. It is very outdated!
def sim_competition(compiler, game, gamedb, token, runs, debug=False, score_func=avg):
    assert gamedb is not None
    assert gamedb.is_comp_token(token)

    seeds = [random() for _ in range(2 * runs + 5)]

    for school in gamedb.get_schools_in_comp(token):
        if debug:
            print("Got school '" + school + "'")
        max_score = 0
        max_code = ""
        for student in gamedb.get_tokens_for_school(school):
            if debug:
                print("Got student '" + student + "'")
            code, options = gamedb.get_code_and_options(student)
            if not code:
                continue
            if debug:
                print("Compiling code...")
            prog = compiler.compile(code)
            prog.options = options
            if debug:
                print("setting up game runner...")
            runner = GameRunner(game)
            if debug:
                print("Simulating...")
            score = None

            scores = []
            count = 0
            seed = 0
#             # TODO: make this able to run in a pool of threads (so it can be run on multiple CPUs)
            while count < runs:
                try:
                    if seed >= len(seeds):
                        print("Ran out of seeds")
                        break
                    scores += [runner.run(Room([prog], seed=seeds[seed]), playback=False).score]
                    # scores += [runner.run_for_avg_score(times=1, seed=seeds[seed])]
                    # print(scores[-1])
                    # import sys
                    # sys.stdout.flush()
                    count += 1
                    seed += 1
                except Exception as e:
                    print("There was an error simulating the game (Moving to next seed):", e)
                    seed += 1
            score = score_func(scores)

            # while score is None:
            #     try:
            #     except Exception as e:
            #         print("There was an error simulating the game:", e)
            if score > max_score:
                max_score = score
                max_code = code
        if debug:
            print("Saving score...", max_score)
        gamedb.set_comp_avg_score(token, school, max_score)
        gamedb.set_comp_school_code(token, school, max_code)
    if debug:
        print("All done :)")


class Ranking(object):
    def __init__(self, bots):
        """

        Args:
            bots: Tuple containing standing and bot id
        """
        self.ranks = {}
        for i in range(0, len(bots)):
            self.ranks[bots[i]] = i  # Key: BOTS Value: RANK

    def __add__(self, other):
        new_rank = {}
        for k in self.ranks:
            new_rank[k] = self.ranks[k] + other[k]
        return new_rank

    def __radd__(self, other):
        if other == 0:
            return self
        new_rank = {}
        for k in self.ranks:
            new_rank[k] = self.ranks[k] + other[k]
        return new_rank

    def add_rank(self, standing, bot):
        self.ranks[bot] += standing


class MultiplayerComp(object):
    def __init__(self, bots, room_size, default_bot_class, run_factor=10):
        """

        Args:
            bots: (PROG) the players program to be executed and ranked
            room_size: (INT) the size of the rooms
            run_factor(int): The average number of games a bot gets to play.
        """
        self.default_bot_class = default_bot_class
        self.room_size = room_size
        self.scores = {}  # Prog:scores
        self.rooms = {}  # Rooms:Rankings
        self.cur_run = 0
        self.total_runs = run_factor * math.ceil(len(bots) / 4.0)
        for bot in bots:
            self.scores[bot] = OnlineMean()

    def __iter__(self):
        return self

    def __setitem__(self, key, value):
        """
        ARGS:
            key (Room): The room to set to ranking
            value (Ranking): The returned ranking
        """
        self.rooms[key] = value
        for k in value.ranks:
            if k.prog in self.scores:
                self.scores[k.prog] += value.ranks[k] * 10

    def __next__(self):
        return self.next()

    def next(self):
        if self.cur_run == self.total_runs:
            raise StopIteration()

        l = list(self.scores.keys())
        shuffle(l)
        p = l[:self.room_size + 1]
        while len(p) < self.room_size:
            p += [self.default_bot_class()]
        room = Room(p)
        self.rooms[room] = None
        self.cur_run += 1
        return room

    @staticmethod
    def sim_multiplayer(s_token, gamedb, game, compiler, save_games=False, debug=False):
        assert game.MULTIPLAYER, "Game must be multi-player to do MultiplayerComp."
        assert gamedb is not None
        assert gamedb.is_school_token(s_token)
        students = gamedb.get_tokens_for_school(s_token)  # Only getting one school token
        bots = []
        game_tokens = []
        for s in students:
            try:
                if debug:
                    print("got student '" + s + "'")
                code, options = gamedb.get_code_and_options(s)
                name = gamedb.get_name(s)
                if not code:
                    continue
                if debug:
                    print("compiling code...")
                prog = compiler.compile(code)
                prog.options = options
                prog.token = s
                prog.name = name
                if debug:
                    print("simulating...")
                bots += [prog]
            except:
                print("Couldn't compile code for '{}' in '{}'".format(s, gamedb.get_school_for_token(s)))
        if len(bots) == 0:
            if debug:
                print("School Token {} has no valid bots. :(".format(s_token))
            return []
        tourney = MultiplayerComp(bots, game.get_number_of_players(), game.default_prog_for_computer())
        for room in tourney:
            if debug:
                print("Room: " + str(room))
            gamerunner = GameRunner(game)
            tourney[room] = gamerunner.run(room).score
            if save_games:
                game_tokens += [room.save(gamedb)]

        for player, score in tourney.scores.items():
            gamedb.save_avg_score(player.token, score.floored_mean)
            if debug:
                print("Score {} for Bike: {}".format(score.mean, str(player.token)))

        return game_tokens


class MultiplayerCompRunner(Process):
    def __init__(self, interval, gamedb, game, compiler, debug=False):
        """

        Args:
            interval(int): The number of seconds between simulating. This is the time between the start of one run and
                the start of the next. Therefore a interval of 0 means when done running once start again.
            gamedb:
            game:
            compiler:
        """
        super(MultiplayerCompRunner, self).__init__()
        self.interval = interval
        self.gamedb = gamedb
        self.game = game
        self.compiler = compiler
        self.start_run = Event()
        self.end = Event()
        self.debug = debug

    def stop(self):
        self.start_run.set()
        self.end.set()

    def run(self):
        while not self.end.is_set():
            if not self.start_run.is_set():
                self.__run()
            self.start_run.wait(self.interval)

    def __run(self):
        print("Scoring all Bots...")
        start_time = time.time()
        gtokens = []
        for s_token in self.gamedb.get_school_tokens():
            gtokens += MultiplayerComp.sim_multiplayer(s_token, self.gamedb, self.game, self.compiler,
                                                       save_games=True, debug=self.debug)
        self.gamedb.replace_games_in_comp(ctoken="P00000000",  # TODO: un hardcode this.
                                          new_gtokens=gtokens)
        print("Finished scoring in {0:.2f} secs...".format(time.time() - start_time))


class RollingMultiplayerComp(object):
    def __init__(self, room_size, default_bot_class, rolling_n):
        """

        Args:
            room_size: (INT) the size of the rooms
            rolling_n: (int) the number of games each players score should be averaged from.
        """
        self.default_bot_class = default_bot_class
        self.room_size = room_size
        self.scores = {}  # type: Dict[Prog, OnlineMean]
        self.rooms = {}  # Rooms:Rankings
        self.rolling_n = rolling_n

        self.bots = set()  # A set of tokens of the already added bots.

    def add_bot(self, bot, gamedb):
        # load old mean
        mean = gamedb.get_value(bot.token, "rolling_score", 0)
        n = gamedb.get_value(bot.token, "rolling_n", 0)
        self.scores[bot] = OnlineMean(n, mean, roll_after_n=self.rolling_n)
        self.bots |= {bot.token}

    def save_rolling_scores(self, gamedb):
        for bot, score in self.scores.items():
            gamedb.save_value(bot.token, "rolling_score", score.mean)
            gamedb.save_value(bot.token, "rolling_n", score.i)
            gamedb.save_avg_score(bot.token, score.floored_mean)

    def add_bot_if_needed(self, bot):
        if bot.token not in self.bots:
            self.add_bot(bot)

    def __iter__(self):
        return self

    def __setitem__(self, key, value):
        """
        ARGS:
            key (Room): The room to set to ranking
            value (Ranking): The returned ranking
        """
        self.rooms[key] = value
        for k in value.ranks:
            if k.prog in self.scores:
                self.scores[k.prog] += value.ranks[k] * 10

    def __next__(self):
        return self.next()

    def next(self):
        l = list(self.scores.keys())
        shuffle(l)
        p = l[:self.room_size + 1]
        while len(p) < self.room_size:
            p += [self.default_bot_class()]
        room = Room(p)
        self.rooms[room] = None
        return room


class RollingMultiplayerCompRunner(Process):
    def __init__(self, interval, gamedb, game, compiler, rolling_n=100, batch_size=4, debug=False):
        """

        Args:
            interval(int): The number of seconds between simulating each game. Should be a pretty small number.
            gamedb:
            game:
            compiler:
        """
        super(RollingMultiplayerCompRunner, self).__init__()

        assert game.MULTIPLAYER, "Game must be multi-player to do MultiplayerComp."
        assert gamedb is not None

        self.interval = interval
        self.gamedb = gamedb
        self.game = game
        self.compiler = compiler
        self.rolling_n = rolling_n
        self.batch_size = batch_size
        self.debug = debug

        self.start_run = Event()
        self.end = Event()

        self.comps = {}  # type: Dict[str, RollingMultiplayerComp]
        self.i = -1  # This is to make the clean happen on the first run. This way it will run at least every time you start the server.

    def stop(self):
        self.start_run.set()
        self.end.set()

    def run(self):
        while not self.end.is_set():
            if not self.start_run.is_set():
                self.__run()
            self.start_run.wait(self.interval)

    def __run(self):
        print("Scoring a couple games...")
        self.i += 1
        start_time = time.time()
        # gtokens = []
        for s_token in self.gamedb.get_school_tokens():
            if s_token not in self.comps:
                self.comps[s_token] = RollingMultiplayerComp(room_size=self.game.get_number_of_players(),
                                                             default_bot_class=self.game.default_prog_for_computer(),
                                                             rolling_n=self.rolling_n)
        for s_token, comp in self.comps.items():
            # First make sure all the bots in the school are in the comp.
            student_tokens = self.gamedb.get_tokens_for_school(s_token)
            for token in student_tokens:
                # only add bot if not already added.
                if token not in comp.bots:
                    bot = self.make_bot(token)
                    if bot:
                        comp.add_bot(bot, self.gamedb)

            if len(comp.bots) == 0:
                if self.debug:
                    print("School Token {} has no valid bots. :(".format(s_token))
                continue  # skip this school if it has no bots to run.

            # Now let's run a couple games.
            for room in islice(comp, self.batch_size):
                if self.debug:
                    print("Room: " + str(room))
                gamerunner = GameRunner(self.game)
                comp[room] = gamerunner.run(room).score

                # save scores and game
                self.gamedb.add_game_to_comp("P00000000", room.save(self.gamedb))
                comp.save_rolling_scores(self.gamedb)

        # TODO: replace this with a function which keeps the last rolling_n number of games for each token.
        # self.gamedb.replace_games_in_comp(ctoken="P00000000",  # TODO: un hardcode this.
        #                                   new_gtokens=gtokens)
        print("Finished scoring games in {0:.2f} secs...".format(time.time() - start_time))
        if self.i % self.rolling_n == 0:
            start_time = time.time()
            print("Will do some clean up....")
            self.clean_up_old_games()
            print("Finished cleaning in {0:.2f} secs...".format(time.time() - start_time))

    def make_bot(self, token):
        try:
            if self.debug:
                print("Making bot for '" + token + "'")
            code, options = self.gamedb.get_code_and_options(token)
            name = self.gamedb.get_name(token)
            if not code:
                return
            if self.debug:
                print("compiling code...")
            prog = self.compiler.compile(code)
            prog.options = options
            prog.token = token
            prog.name = name
            return prog
        except:
            print("Couldn't compile code for '{}' in '{}'".format(s, gamedb.get_school_for_token(s)))

    def clean_up_old_games(self):
        # Since we keep making new games we should clean up the old ones.
        # Only keep the newest `rolling_n` number of games for each player
        all_game_tokens = set(self.gamedb.get_games_for_token("P00000000"))
        games_to_delete = set(all_game_tokens)

        for s_token in self.gamedb.get_school_tokens():
            for token in self.gamedb.get_tokens_for_school(s_token):
                games = set(self.gamedb.get_games_for_token(token))
                games = games.intersection(all_game_tokens)  # only keep the games that were used for scoring.
                if self.rolling_n >= len(games):  # We need to keep them all
                    games_to_delete = games_to_delete - games
                else:  # This player has too many games.
                    # We need to pick the newest ones
                    games = list(games)
                    games.sort(key=lambda x: self.gamedb.get_ctime_for_game(x), reverse=True)
                    games_player_needs = games[:self.rolling_n]
                    games_to_delete = games_to_delete - set(games_player_needs)

        if self.debug:
            print("Cleaning up {} games...".format(len(games_to_delete)))

        for gtoken in games_to_delete:
            self.gamedb.delete_game(gtoken)

    # def clean_up_broken_games(self):
    #     all_recorded_games = set(self.gamedb.get_all_game_tokens())
    #     for s_token in self.gamedb.get_school_tokens():
    #         for token in self.gamedb.get_tokens_for_school(s_token):
    #             for game_token in self.gamedb.get_games_for_token(token):
    #                 if game_token not in all_recorded_games:
    #                     print("This is bad!!!")
    #     for comp_token in self.gamedb.get_all_comp_tokens():
    #         for game_token in self.gamedb.get_games_for_token(token):
    #             if game_token not in all_recorded_games:
    #                 print("This is bad!!!")

