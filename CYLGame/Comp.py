from __future__ import print_function
from .Game import GameRunner
from .Player import Room
from random import random, choice


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


def create_room_for_school(gamedb, stoken):
    # TODO: write this.
    raise Exception("Not Implemented!")


def avg(scores):
    return float((sum(scores) * 100) / len(scores)) / 100


def sim_competition(compiler, game, gamedb, token, runs, debug=False, score_func=avg):
    assert gamedb is not None
    assert gamedb.is_comp_token(token)

    seeds = [random() for _ in xrange(2*runs+5)]

    for school in gamedb.get_schools_in_comp(token):
        if debug:
            print("Got school '" + school + "'")
        max_score = 0
        max_code = ""
        for student in gamedb.get_tokens_for_school(school):
            if debug:
                print("Got student '" + student + "'")
            code = gamedb.get_code(student)
            if not code:
                continue
            if debug:
                print("Compiling code...")
            prog = compiler.compile(code.split("\n"))
            if debug:
                print("Setting up game runner...")
            runner = GameRunner(game, prog)
            if debug:
                print("Simulating...")
            score = None

            scores = []
            count = 0
            seed = 0
            # TODO: make this able to run in a pool of threads (So it can be run on multiple CPUs)
            while count < runs:
                try:
                    if seed >= len(seeds):
                        print("Ran out of seeds")
                        break
                    scores += [runner.run_for_avg_score(times=1, seed=seeds[seed])]
                    # print(scores[-1])
                    # import sys
                    # sys.stdout.flush()
                    count += 1
                    seed += 1
                except Exception as e:
                    print("There was an error simulating the game (Moving to next seed):", e)
                    seed += 1
            score = score_func(scores)
            # score = runner.run_for_avg_score(times=runs)

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
