from __future__ import division, print_function

from typing import Dict

import math
import sys
import time
from itertools import islice
from multiprocessing import Event, Pool, Process
from random import choice, randint, shuffle

from CYLGame.Utils import OnlineMean, choose

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
        code, options = gamedb.get_active_code_and_options(token)
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


def sim_prog_for_score(game, compiler, code, options, seed, debug=True):
    runner = GameRunner(game)
    prog = compiler.compile(code)
    prog.options = options
    try:
        score = runner.run(Room([prog], seed=seed), playback=False).score
        sys.stdout.write(".")
        sys.stdout.flush()
        return score
    except:
        print(
            "There was an error simulating the game. Make sure this isn't a bug with the program.\n  Seed: {}\n  Code: '''{}'''".format(
                seed, code
            )
        )
        return 0


# TODO: rewrite this function. It is very outdated!
def sim_competition(compiler, game, gamedb, token, runs, ncores=None, debug=False, score_func=avg):
    """

    Args:
        compiler:
        game:
        gamedb:
        token:
        runs:
        ncores:      If None will default to the number of all available cores.
        debug:
        score_func:

    Returns:

    """
    assert gamedb is not None
    assert gamedb.is_comp_token(token)

    seeds = [randint(0, sys.maxsize) for _ in range(runs)]

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
                print("Simulating {} games...".format(runs))

            #             # TODO: make this able to run in a pool of threads (so it can be run on multiple CPUs)
            with Pool(processes=ncores) as pool:
                scores = pool.starmap(
                    sim_prog_for_score, [(game, compiler, code, options, seed, debug) for seed in seeds]
                )

            score = score_func(scores)
            if debug:
                print(" Score: {}".format(score))

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
            run_factor(int): The average number of random games per combination of bots.
        """
        self.default_bot_class = default_bot_class
        self.room_size = room_size
        self.scores = {}  # Prog:scores
        self.rooms = {}  # Rooms:Rankings
        self.cur_run = 0
        self.total_runs = run_factor * choose(max(len(bots), 4), 4)
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

    def __getitem__(self, item):
        return self.scores[item]

    def __next__(self):
        return self.next()

    def next(self):
        if self.cur_run == self.total_runs:
            raise StopIteration()

        l = list(self.scores.keys())
        shuffle(l)
        p = l[: self.room_size + 1]
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

    @staticmethod
    def make_bot(gamedb, compiler, token, debug=False):
        try:
            if debug:
                print("Making bot for '" + token + "'")
            code, options = gamedb.get_active_code_and_options(token)
            name = gamedb.get_name(token)
            if not code:
                return
            if debug:
                print("compiling code...")
            prog = compiler.compile(code)
            prog.options = options
            prog.token = token
            prog.name = name
            return prog
        except:
            print("Couldn't compile code for '{}' in '{}'".format(s, gamedb.get_school_for_token(s)))

    @staticmethod
    def sim_comp(c_token, gamedb, game, compiler, save_games=False, debug=False):
        if debug:
            print("Getting the best bots from each school...")

        # Get the best valid bot
        best_bots = {}
        for s_token in gamedb.get_schools_in_comp(c_token):
            best_bot = None
            best_bot_score = float("-inf")
            for token in gamedb.get_tokens_for_school(s_token):
                if gamedb.get_avg_score(token, float("-inf")) > best_bot_score:
                    bot = MultiplayerComp.make_bot(gamedb, compiler, token, debug=debug)

                    if bot:
                        # Was compilable and the best bot
                        best_bot_score = gamedb.get_avg_score(token)
                        best_bot = bot
            if best_bot:
                best_bots[s_token] = best_bot
            elif debug:
                print(f"School {s_token} had on bot with a score")

        if debug:
            print(f"Got the following bots:\n{best_bots}")

        if len(best_bots) == 0:
            if debug:
                print("No School had any valid bots. :(")
            return

        game_tokens = []
        tourney = MultiplayerComp(best_bots.values(), game.get_number_of_players(), game.default_prog_for_computer())
        if debug:
            print(f"Will run {tourney.total_runs:.0f} games.")
        start_time = time.time()
        for i, room in enumerate(tourney):
            if debug:
                time_taken = time.time() - start_time
                estimate_total_time = time_taken * (tourney.total_runs / (i + 1))
                eta = estimate_total_time - time_taken
                print(f"Eta: ~{eta:.0f} secs Cur Room: {room}")
            gamerunner = GameRunner(game)
            tourney[room] = gamerunner.run(room).score
            if save_games:
                game_tokens += [room.save(gamedb)]

        if save_games:
            gamedb.replace_games_in_comp(c_token, new_gtokens=save_games)

        # Save scores
        for s_token, best_bot in best_bots.items():
            best_bot_score = tourney[best_bot].rounded_mean()
            gamedb.set_comp_avg_score(c_token, s_token, best_bot_score)


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
            gtokens += MultiplayerComp.sim_multiplayer(
                s_token, self.gamedb, self.game, self.compiler, save_games=True, debug=self.debug
            )
        self.gamedb.replace_games_in_comp(ctoken="P00000000", new_gtokens=gtokens)  # TODO: un hardcode this.
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

    def add_bot_if_needed(self, bot, gamedb):
        if bot.token not in self.bots:
            self.add_bot(bot, gamedb)

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
        p = l[: self.room_size + 1]
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
        self.i = (
            -1
        )  # This is to make the clean happen on the first run. This way it will run at least every time you start the server.

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
                self.comps[s_token] = RollingMultiplayerComp(
                    room_size=self.game.get_number_of_players(),
                    default_bot_class=self.game.default_prog_for_computer(),
                    rolling_n=self.rolling_n,
                )
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
            code, options = self.gamedb.get_active_code_and_options(token)
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
                    games_player_needs = games[: self.rolling_n]
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
