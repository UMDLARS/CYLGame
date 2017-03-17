from __future__ import print_function
from Game import GameRunner


def sim_competition(compiler, game, gamedb, token, runs, debug=False):
    assert gamedb is not None
    assert gamedb.is_comp_token(token)

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
            score = runner.run_for_avg_score(times=runs)
            if score > max_score:
                max_score = score
                max_code = code
        if debug:
            print("Saving score...")
        gamedb.set_comp_avg_score(token, school, max_score)
        gamedb.set_comp_school_code(token, school, max_code)
    if debug:
        print("All done :)")
