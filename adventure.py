#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maze - Projekt
"""

import maze
import re
import sys
import getopt
import os.path

def main():
    """
    Main method, starts program
    """
    try:
        opts, _ = getopt.gnu_getopt(
            sys.argv[1:], 'hivacl:', ['help', 'info', 'load=', 'version', 'about', 'cheat']
            )
    except getopt.GetoptError as error:
        print(error)
        print_usage()

    # Setup default parameter 'game_file' to include calling Game constructor
    params = {'game_file': None}

    # Parse options from command prompt. If multiple are given, act on the first found
    # The statements isn't "else checked" but each method will do sys.exit()
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_usage()
        if opt in ('-i', '--info'):
            print_info()
        if opt in ('-v', '--version'):
            print_version()
        if opt in ('-a', '--about'):
            print_about()
        if opt in ('-c', '--cheat'):
            print_cheats()

        # Check if a file given to load actually exists
        if opt in ('-l', '--load'):
            if not os.path.isfile(arg):
                print("File {!s} not found!".format(arg))
                sys.exit(0)

            params['game_file'] = arg

    # No parameter that will terminate the program given, start the game
    run_game(params)
    sys.exit(0)

def run_game(params):
    """
    The main loop keeping the game alive
    """
    # Create default Game object
    g = maze.Game(params)

    # No need to print the info if a user previously played
    if g.game_file == None:
        g.print_game_info()
        print()

    g.print_room_info()

    while True:
        if g.game_completed == True:
            return

        user_input = input(">>> ")

        # Check if the user input was a single letter/word and act on it
        if user_input in ('i', 'info'):
            g.print_room_info()
        elif user_input in ('h', 'hjälp', 'help'):
            g.print_help()
        elif user_input in ('fr', 'fram', 'forward'):
            g.goto_next_room()
        elif user_input in ('ba', 'bak', 'back'):
            g.goto_prev_room()
        elif user_input in ('se', 'look'):
            g.look_around() # Should describe room?
        elif user_input in ('l', 'ledtråd', 'hint'):
            g.print_hint()
        elif user_input in ('objekt', 'o'):
            g.look_around()
        elif user_input in ('inv', 'inventarier'):
            g.list_inventory()
        elif user_input in ('spara', 'sp', 'save'):
            g.save_game()
        elif user_input in ('q', 'quit'):
            break

        # Parse input to find action and object
        input_re = re.compile(r'^(\w+) (.+)$')
        input_match = input_re.search(user_input)

        # Check that we even got a match (two words)
        if input_match == None:
            continue

        # Check that both groups are assigned
        if input_match.group(2) == None:
            continue

        # Save the action and original object (to print according to user input)
        (action, orig_obj) = (input_match.group(1), input_match.group(2))

        # Strip user input and make it lowercase
        obj = orig_obj.lower()
        obj = re.sub(r"['\.]", "", obj, flags=re.IGNORECASE)

        # Actions you can do with inventory
        inv_actions = ['sl', 'släpp', 'drop',
                       'a', 'användä', 'use']

        # Actions you can do with objects
        obj_actions = ['t', 'titta', 'see',
                       'ö', 'öppna', 'open',
                       's', 'sparka', 'kick',
                       'f', 'flytta', 'move',
                       'ta', 'take']

        if action not in inv_actions and action not in obj_actions:
            print("I don't know what you men by '{!s}'... Type 'help' to see what you can do.".format(action))
            continue

        if action in inv_actions and obj not in g.inventory:
            print("Hmm, I can't see {!s} in the inventory...".format(orig_obj))
            continue

        if action in obj_actions and obj not in g.current_room['objects']:
            print("There's no {!s} in this room!".format(orig_obj))
            continue

        # Based on action, send the object to relevant method in Game
        if action in ('t', 'titta', 'see'):
            g.look_at_object(obj)
        elif action in ('ö', 'öppna', 'open'):
            g.open_object(obj, None)
        elif action in ('s', 'sparka', 'kick'):
            g.kick_object(obj, None)
        elif action in ('f', 'flytta', 'move'):
            g.move_object(obj, None)
        elif action in ('ta', 'take'):
            g.take_object(obj)
        elif action in ('sl', 'släpp', 'drop'):
            g.drop_object(obj, None)
        elif action in ('a', 'använd', 'use'):
            g.use_object(obj)

def print_usage():
    """
    Prints usage/help for porgram
    """
    print("Usage: {!s}\n".format(sys.argv[0]))
    print("{: <10} | {: <4} - {!s}".format("--help", "-h", "Print this help text"))
    print("{: <10} | {: <4} - {!s}".format("--info", "-i", "Print info about the game"))
    print("{: <10} | {: <4} - {!s}".format("--version", "-v", "Print version of the program"))
    print("{: <10} | {: <4} - {!s}".format("--about", "-a", "Print information about the developer"))
    print("{: <10} | {: <4} - {!s}".format("--cheat", "-c", "Print available cheats and tricks"))
    print("{: <10} | {: <4} - {!s}".format("--load", "-l", "Load game from save file"))
    sys.exit(0)

def print_info():
    """
    Information about the program
    """
    print(r"""- INFO -
This is the text based game called adventure.py! In the game the user is taken through
several rooms and by moving, kicking or opening objects found around in the game, the player
will be able to open up new paths to discover the next room.

To make it possible to complete the game, the player is equipped with a backpack (inventory)
that can hold stuff picked up in the game.""")
    sys.exit(0)

def print_version():
    """
    Print current version
    """
    print(r"""- VERSION -
0.2b""")
    sys.exit(0)

def print_about():
    """
    Information about the developer
    """
    print(r"""- ABOUT -
This game is developed by Simon Sawert
""")
    sys.exit(0)

def print_cheats():
    """
    Cheats that can be used in the game
    """
    print("- CHEATS -")

    # Game has an option to print every room and it's object so we call it
    g = maze.Game({'game_file': None})
    g.print_game_objects()

    # Added this manually, didn't figure out a way to do this automatically
    # and I guess this is only used for the teacher correcting the task
    print(r"""
Copy/paste to complete the game:

s mirror
s photo frame
ta wardrobe key
ta shattered glass
a wardrobe key
fr
a shattered glass
ta zippo
f drawer
a zippo
fr
ta remote
a remote
ta door key
a door key
fr
s globe
ta toy car
a toy car
fr
f gurney
ta scalpel
a scalpel
ta small key
a small key
fr
f pillars
ta hammer
a hammer
ta crowbar
a crowbar
fr
ö knight's helmet
ta silver key
ba
ba
ba
a silver key
ta stone
fr
fr
fr
a stone
ta gate key
# a gate key # - This completes the game
""")

    sys.exit(0)

if __name__ == '__main__':
    main()
