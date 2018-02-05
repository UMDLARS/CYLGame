#!/usr/bin/python
from __future__ import print_function
import os
import sys
from CYLGame.Database import GameDB
from builtins import input

gamedb = None
cur_school = None
cur_comp = None


def clear():
    os.system("clear")


def pause(prompt="Enter any input: "):
    get_input(prompt, lambda x: 1)


def get_input(prompt="", validator=lambda x: x, error_msg=""):
    inp = input(prompt)
    while not validator(inp):
        print(error_msg)
        inp = input(prompt)
    return inp


def print_menu(options=[], title=""):
    clear()
    print(title)
    for index, option in enumerate(options):
        print(str(index+1)+":", option)
    return int(get_input("Select an item: ", lambda x: int(x) in range(1,len(options)+1), "Invalid Selection. Try Again."))-1


def clear_selection():
    global cur_comp, cur_school
    cur_comp = None
    cur_school = None


def add_competition():
    global gamedb, cur_comp
    clear()
    comp_name = get_input("Enter New Competition Name: ")
    # TODO(derpferd): add school selection
    # TODO(derpferd): add token selection from school
    clear_selection()
    cur_comp = gamedb.add_new_competition(comp_name)

    # # select the top scoring bots from each school
    # for school in gamedb.get_school_tokens():
    #     top_bot = None
    #     top_score = -1
    #     for user in gamedb.get_tokens_for_school(school):
    #         score = gamedb.get_avg_score(user)
    #         if score is None:
    #             score = 0
    #         if score > top_score:
    #             top_score = score
    #             top_bot = user
    #     if top_bot is not None:
    #         gamedb.set_token_for_comp(token, top_bot, school)

    print("Don't forget to run competition sim script with the following token:", cur_comp)
    pause()


def select_competition():
    # TODO(derpferd): implement
    global gamedb, cur_comp
    options = []
    options_to_tokens = {}
    for i, comp_tk in enumerate(gamedb.get_comp_tokens()):
        options += [gamedb.get_name(comp_tk)]
        options_to_tokens[i] = comp_tk
    clear_selection()
    cur_comp = options_to_tokens[print_menu(options, "Select Competition")]
    print("Current Competition Set to:", cur_comp)


def add_school_to_comp():
    global gamedb, cur_comp
    options = []
    options_to_tokens = {}
    for i, school_tk in enumerate(gamedb.get_school_tokens()):
        options += [gamedb.get_name(school_tk)]
        options_to_tokens[i] = school_tk
    selection = options_to_tokens[print_menu(options, "Select School")]
    gamedb.add_school_to_comp(cur_comp, selection)
    print("School added")
    print("Don't forget to run competition sim script with the following token:", cur_comp)
    pause()


def list_schools_in_comp():
    global gamedb, cur_comp
    clear()
    print("Schools")
    for token in gamedb.get_schools_in_comp(cur_comp):
        print(gamedb.get_name(token))
    pause()


# TODO(derpferd): add function to remove a school


def add_school():
    global gamedb, cur_school
    clear()
    school_name = get_input("Enter New School Name: ")
    clear_selection()
    cur_school = gamedb.add_new_school(school_name)
    print("Current School Set to:", cur_school)


def select_school():
    global gamedb, cur_school
    options = []
    options_to_tokens = {}
    for i, school_tk in enumerate(gamedb.get_school_tokens()):
        options += [gamedb.get_name(school_tk)]
        options_to_tokens[i] = school_tk
    clear_selection()
    cur_school = options_to_tokens[print_menu(options, "Select School")]
    print("Current School Set to:", cur_school)


def get_new_tokens():
    global gamedb, cur_school
    clear()
    count = int(get_input("How many tokens would you like: ", lambda x: x.isdigit(), "Please enter a number."))
    clear()
    print("New tokens")
    for _ in range(count):
        print(gamedb.get_new_token(cur_school))

    pause()


def list_tokens():
    global gamedb, cur_school
    clear()
    print("Tokens")
    for token in gamedb.get_tokens_for_school(cur_school):
        print(token)

    pause()


def get_main_menu_options():
    global cur_school
    options = ["Add New School", "Select School", "Add New Competition", "Select Competition"]
    if cur_school is not None:
        options += ["Get new Tokens", "List current Tokens"]
    if cur_comp is not None:
        # TODO(derpferd): implement
        options += ["Add School to Competition", "List Schools in Competition"]
    return options + ["Quit"]


def get_main_menu_title():
    global gamedb, cur_school, cur_comp
    title = "Main Menu"
    if cur_school is not None:
        title += "\n\nSelected School: "+gamedb.get_name(cur_school)+" ("+cur_school+")"
    if cur_comp is not None:
        title += "\n\nSelected Competition: "+gamedb.get_name(cur_comp)+" ("+cur_comp+")"
    return title


def main():
    global gamedb
    print("Welcome to the GameDB Editor")
    print("!!!!WARNING!!!!!!")
    print("If you do NOT know what you are doing. Please exit now!!!")
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        game_path = os.path.abspath(sys.argv[1])
        print("You choose", game_path, "as a game path.")
    else:
        game_path = os.path.abspath(get_input("Your current dir is '"+os.path.abspath(os.curdir)+"'\nEnter path to game dir: ", lambda x: os.path.exists(x), error_msg="Invalid Game Directory. Try Again."))
    gamedb = GameDB(game_path)
    option = ""
    while option != "Quit":
        options = get_main_menu_options()
        option = options[print_menu(options, get_main_menu_title())]
        print("You selected:", option)
        if option == "Select School":
            select_school()
        elif option == "Select Competition":
            select_competition()
        elif option == "Add New Competition":
            add_competition()
        elif option == "Add School to Competition":
            add_school_to_comp()
        elif option == "List Schools in Competition":
            list_schools_in_comp()
        elif option == "Add New School":
            add_school()
        elif option == "Get new Tokens":
            get_new_tokens()
        elif option == "List current Tokens":
            list_tokens()


if __name__ == '__main__':
    main()
