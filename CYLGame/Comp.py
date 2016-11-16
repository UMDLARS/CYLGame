from __future__ import print_function
from Game import GameRunner


def sim_competition(compiler, game, gamedb, token, runs, debug=False):
    assert gamedb is not None
    assert gamedb.is_comp_token(token)

    for school in gamedb.get_schools_in_comp(token):
        if debug:
            print("Got school '" + school + "'")
        code = gamedb.get_comp_code(token, school)
        if debug:
            print("Compiling code...")
        prog = compiler.compile(code.split("\n"))
        if debug:
            print("Setting up game runner...")
        runner = GameRunner(game, prog)
        if debug:
            print("Simulating...")
        score = runner.run_for_avg_score(times=runs)
        if debug:
            print("Saving score...")
        gamedb.set_comp_avg_score(token, school, score)
    if debug:
        print("All done :)")
