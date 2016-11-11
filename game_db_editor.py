#!/usr/bin/python
from __future__ import print_function
import os
from CYLGame.Database import GameDB

gamedb = None
cur_school = None


def clear():
    os.system("clear")


def get_input(prompt="", validator=lambda x: x, error_msg=""):
    inp = None
    err = ""
    while not inp or not validator(inp):
        print(err)
        inp = raw_input(prompt)
    return inp


def print_menu(options=[], title=""):
    clear()
    print(title)
    for index, option in enumerate(options):
        print(str(index+1)+":", option)
    return int(get_input("Select an item: ", lambda x: int(x) in range(1,len(options)+1), "Invalid Selection. Try Again."))-1


def add_school():
    global gamedb, cur_school
    clear()
    school_name = get_input("Enter New School Name: ")
    cur_school = gamedb.add_new_school(school_name)
    print("Current School Set to:", cur_school)


def select_school():
    global gamedb, cur_school
    options = []
    options_to_tokens = {}
    for i, school_tk in enumerate(gamedb.get_school_tokens()):
        options += [gamedb.get_name(school_tk)]
        options_to_tokens[i] = school_tk
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

    get_input("Copy tokens then enter any input: ")


def list_tokens():
    global gamedb, cur_school
    clear()
    print("Tokens")
    for token in gamedb.get_tokens_for_school(cur_school):
        print(token)

    get_input("Enter any input: ")


def get_main_menu_options():
    global cur_school
    options = ["Add New School", "Select School"]
    if cur_school is not None:
        options += ["Get new Tokens", "List current Tokens"]
    return options + ["Quit"]


def get_main_menu_title():
    global gamedb, cur_school
    title = "Main Menu"
    if cur_school is not None:
        title += "\n\nSelected School: "+gamedb.get_name(cur_school)+" ("+cur_school+")"
    return title


def main():
    global gamedb
    print("Welcome to the GameDB Editor")
    print("!!!!WARNING!!!!!!")
    print("If you do NOT know what you are doing. Please exit now!!!")
    game_path = os.path.abspath(get_input("Your current dir is '"+os.path.abspath(os.curdir)+"'\nEnter path to game dir: ", lambda x: os.path.exists(x), error_msg="Invalid Game Directory. Try Again."))
    gamedb = GameDB(game_path)
    option = ""
    while option != "Quit":
        options = get_main_menu_options()
        option = options[print_menu(options, get_main_menu_title())]
        print("You selected:", option)
        if option == "Select School":
            select_school()
        elif option == "Add New School":
            add_school()
        elif option == "Get new Tokens":
            get_new_tokens()
        elif option == "List current Tokens":
            list_tokens()


if __name__ == '__main__':
    main()
