#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Maze - The class package to keep the game alive

The class is based on a JSON file holding information about the game,
inventory and rooms. This means that anyone can create more rooms,
objects or items and run it through this class.
"""

import random
import json
import os.path
import room_ascii

class Game:
    """
    Maze object - Game
    """
    def __init__(self, args):
        """
        Init method - Will load the game template from a json file
        """
        self.game_completed = False
        self.game_file = args['game_file']
        self.game = self._setup_game()

        self.current_room = self.game['rooms'][str(self.game['current_room_id'])]
        self.can_continue = True if self.game['highest_room_id'] > self.game['current_room_id'] else False
        self.inventory = self.game['inventory']

    def print_game_info(self):
        """
        The starting text of the game
        """
        print(r"""
88888888888 888                    888b     d888                            
    888     888                    8888b   d8888                            
    888     888                    88888b.d88888                            
    888     88888b.   .d88b.       888Y88888P888  8888b.  88888888  .d88b.  
    888     888 "88b d8P  Y8b      888 Y888P 888     "88b    d88P  d8P  Y8b 
    888     888  888 88888888      888  Y8P  888 .d888888   d88P   88888888 
    888     888  888 Y8b.          888   "   888 888  888  d88P    Y8b.     
    888     888  888  "Y8888       888       888 "Y888888 88888888  "Y8888

                                                          © Simon Sawert
""")
        print(self.game['start_text'])

    def print_room_info(self):
        """
        Print information about the room the player is currently in
        """
        print("You're in room number {0}. {1}".format(self.current_room['number'], self.current_room['info']))
        print(room_ascii.get_room_art(self.current_room['number']))

    def print_help(self):
        """
        Print available commands
        """
        print("Available commands for {!s}".format(self.game['game_name']))

        print("{: <12} | {: <4} - {!s}".format("info", "i", "Print this help text"))
        print("{: <12} | {: <4} - {!s}".format("fram", "fr", "Go forward to next room"))
        print("{: <12} | {: <4} - {!s}".format("bak", "bk", "Go backwards to previous room"))
        print("{: <12} | {: <4} - {!s}".format("se", "", "Look around in the room"))
        print("{: <12} | {: <4} - {!s}".format("ledtråd", "l", "List hints inside the room"))
        print("{: <12} | {: <4} - {!s}".format("quit", "q", "Quit the game"))
        print("{: <12} | {: <4} - {!s}".format("spara", "sp", "Save your progress"))

        print()
        print("---")
        print("You can try to interact with objects inside the room")

        print("{: <12} | {: <4} - {!s}".format("objekt", "o", "List objects inside the room"))
        print("{: <12} | {: <4} - {!s}".format("titta", "t", "Look att [object]"))
        print("{: <12} | {: <4} - {!s}".format("öppna", "ö", "Open [object], if possible"))
        print("{: <12} | {: <4} - {!s}".format("sparka", "s", "Kick [object], if possible"))
        print("{: <12} | {: <4} - {!s}".format("flytta", "f", "Move [object], if possible"))

        print()
        print("---")
        print("You can carry items along your jorney")
        print("{: <12} | {: <4} - {!s}".format("inventarier", "inv", "List your current inventory"))
        print("{: <12} | {: <4} - {!s}".format("ta", "", "Take [object]"))
        print("{: <12} | {: <4} - {!s}".format("släpp", "sl", "Drop [object]"))
        print("{: <12} | {: <4} - {!s}".format("använd", "a", "Use [object]"))

        print()
        print("Hint - All commands have an english equivalent command (like kick, open, drop etc)")

    def goto_next_room(self):
        """
        Try to go to the next room
        """
        if self.can_continue == False:
            print("You can't go on just yet, the path to the next room is still blocked!")
            return

        next_room = self.current_room['number'] + 1
        self.current_room = self.game['rooms'][str(next_room)]

        # If the next room is the highest visited room, the player must solve the room
        # mysteries before continuing
        if next_room >= self.game['highest_room_id']:
            self.can_continue = False
            self.game['highest_room_id'] = next_room

        self.game['current_room_id'] = next_room
        self.print_room_info()

    def goto_prev_room(self):
        """
        Try to go to the previous room
        """
        prev_room = self.current_room['number'] - 1

        if prev_room < 1:
            print("You're at the first room, you can't go any further back...")
            return

        # Even if the current room was cleared or not, a player must be able
        # to move forward again after moving to previous room
        self.can_continue = True
        self.game['current_room_id'] = prev_room

        self.current_room = self.game['rooms'][str(prev_room)]
        self.print_room_info()

    def look_around(self):
        """
        Look around in the current room
        """
        # Remove hidden objects when the user looks around
        visible_objects = {}
        for k, v in self.current_room['objects'].items():
            if 'hidden' in v and v['hidden'] == True:
                continue

            visible_objects[k] = v

        print("There are {0} items in the room:".format(len(visible_objects)))

        for obj in visible_objects:
            data = visible_objects[obj]
            print("{!s} - {!s}".format(data['name'], data['desc']))

    def print_hint(self):
        """
        Show some hints about the room
        """
        # Not all objects have a hint so check all objects to see if they do
        # If so, add the hint to a new list
        hints = []
        for obj in self.current_room['objects']:
            data = self.current_room['objects'][obj]
            if 'hint' in data:
                hints.append(data['hint'])

        if len(hints) < 1:
            print("Sorry, there are no hints to give for this room...")
            return

        # Get a random hint from the generated list
        hint = hints[random.randint(0, len(hints) - 1)]
        print(hint)

    def look_at_object(self, obj):
        """
        Inspect given object
        """
        print("Looking at the {!s}...".format(obj))
        print("{!s}".format(self.current_room['objects'][obj]['desc']))

    def open_object(self, obj, force):
        """
        Open an object
        """
        # We can force to open an object internally, this is used
        # when a 'use' action is made in the room
        if force == None:
            if self.current_room['objects'][obj]['openable'] == False:
                print("Hmmm... It seems impossible to open this {!s}".format(obj))
                return

        print("You opened the {!s}!".format(obj))
        print("{!s}".format(self.current_room['objects'][obj]['open_event']))

        # Check if the object has something inside and add it to the room
        self._add_found_item(obj)

    def kick_object(self, obj, force):
        """
        Kick an object
        """
        if force == None:
            if self.current_room['objects'][obj]['breakable'] == False:
                print("Hmmm... It seems impossible to break this {!s}".format(obj))
                return

        print("You broke the {!s}!".format(obj))
        print("{!s}".format(self.current_room['objects'][obj]['break_event']))

        self._add_found_item(obj)

    def move_object(self, obj, force):
        """
        Move an object
        """
        if force == None:
            if self.current_room['objects'][obj]['moveable'] == False:
                print("I don't see a way to move the {!s}".format(obj))
                return

        print("You moved the {!s}".format(obj))
        print("{!s}".format(self.current_room['objects'][obj]['move_event']))

        self._add_found_item(obj)

    def _add_found_item(self, obj):
        """
        Add the item that was found or created by opening or breaking another object
        """
        # Check if something was inside the opened/broken/moved object
        if 'inside' in self.current_room['objects'][obj]:
            inside = self.current_room['objects'][obj]['inside']

            # It can be another object to interact with
            if inside['type'] == 'object':
                inside['usable_at'] = None
                inside['usable_in'] = None

            # Or it can be an item (that can be picked up and later used)
            item_inside = {
                'name': inside['name'],
                'desc': inside['desc'],
                'usable_at': inside['usable_at'],
                'usable_in': inside['usable_in'],
                'openable': False,
                'breakable': False,
                'moveable': False,
                'takeable': True,
            }

            object_inside = inside

            if inside['type'] == 'item':
                self.current_room['objects'][inside['name'].lower()] = item_inside
            else:
                self.current_room['objects'][inside['name'].lower()] = object_inside

        # After the inside is revealed, transform the object to it's final state
        self._transform_to_final_state(obj)

        return

    def _transform_to_final_state(self, obj):
        """
        Transform an object to it's final state
        """
        # If an object doesn't have a final state, just remove it
        if 'final_state' not in self.current_room['objects'][obj]:
            self.current_room['objects'].pop(obj, None)
            return

        # Store the final state and remove the original object
        final_state = self.current_room['objects'][obj]['final_state']
        self.current_room['objects'].pop(obj, None)

        # Replace with the object in final state. These object can never be interacted
        # with since they're in the FINAL state
        self.current_room['objects'][final_state['name'].lower()] = {
            'name': final_state['name'],
            'desc': final_state['desc'],
            'openable': False,
            'breakable': False,
            'moveable': False,
            'takeable': False,
        }

        return

    def list_inventory(self):
        """
        List what the user is currently carrying
        """
        # Check if there are any item's at all
        if len(self.inventory) < 1:
            print("There are no items in the inventory... Things can be picked up using 'ta [obj]'")
            return

        for item in self.inventory:
            data = self.inventory[item]
            print("{!s} - {!s}".format(data['name'], data['desc']))


    def take_object(self, obj):
        """
        Take an object
        """
        if self.current_room['objects'][obj]['takeable'] == False:
            print("Uff! It isn't really necessary to take the {!s}".format(obj))
            return

        # Put the object as is in the inventory and remove it from the room
        print("This {!s} must be usable later, let's keep it!".format(obj))
        self.inventory[obj] = self.current_room['objects'][obj]
        self.current_room['objects'].pop(obj, None)


    def drop_object(self, obj, forever):
        """
        Drop an object from the inventory
        """
        print("Well... Guess there's no need to keep carrying this {!s} around".format(obj))

        # An object can be dropped forever so it can't be picked up again
        # This is made when there's no longer a use for it. If the player
        # want's to drop it, it will continue to exist in the room it was dropped
        if forever == None:
            self.current_room['objects'][obj] = self.inventory[obj]

        # Remove the object from the inventory
        self.inventory.pop(obj, None)

    def use_object(self, obj):
        """
        Use a previously picked up item
        """
        # Object must be in inventory to be used
        if obj not in self.inventory:
            print("There's no {!s} to use in the inventory!".format(obj))
            return

        # It must be used in designated room
        if self.inventory[obj]['usable_in'] != self.current_room['number']:
            print("I don't think this {!s} should be used in this room, it's probably somewhere else".format(
                self.inventory[obj]['name']))
            return

        usable_at = self.inventory[obj]['usable_at']

        # Sometimes the use object can be hidden or not yet revealed. If that happens,
        # hint the user that it should be in this room but say it doesn't exist (yet)
        if self.inventory[obj]['usable_at'] not in self.current_room['objects']:
            print(r"""Strange. I'm pretty sure this {!s} should be used
in this room, however I can't find where to use it at""".format(obj))
            return

        print("You used the {!s}...".format(obj))
        event = self.current_room['objects'][usable_at]['use_event']

        # When an object is used, the item it's used at should have an event type
        # 'game_cleared': Game is cleared
        # 'continue': The event triggered something that made the player able to continue
        # 'move': The event triggered smoething to move
        # 'break': The event triggered something to break (usually a tool/weapon)
        # 'open': The event triggered something to open (usually a key)
        # Always perform these action with FORCE
        if event == 'game_cleared':
            self._end_game()
        elif event == 'continue':
            self.can_continue = True
            print("{!s}".format(self.current_room['objects'][usable_at]['continue_event']))
            self._transform_to_final_state(usable_at)
            print(" *** The next room is now unlocked, you can now keep your adventure!")
        elif event == 'move':
            self.move_object(usable_at, 1)
        elif event == 'break':
            self.kick_object(usable_at, 1)
        elif event == 'open':
            self.open_object(usable_at, 1)

        # Auto drop an object forever if it's been used
        self.drop_object(obj, 1)
   
    def print_game_objects(self):
        """
        Print a summary of all objects in all rooms and how the are being interacted with
        """
        for room, data in sorted(self.game['rooms'].items()):
            print("Info about room {!s}".format(room))

            # Add attributes based on the object data
            for obj in data['objects']:
                info = data['objects'][obj]
                attributes = []
    
                if info['breakable'] == True:
                    attributes.append("can be kicked")

                if info['takeable'] == True:
                    attributes.append("can be taken")

                if info['openable'] == True:
                    attributes.append("can be opened")

                if info['moveable'] == True:
                    attributes.append("can be moved")

                if len(attributes) < 1:
                    attributes.append("is being interacted with using another items")

                if 'hidden' in info and info['hidden'] == True:
                    attributes.append("is hidden")

                if 'inside' in info:
                    if info['inside']['type'] == 'item':
                        attributes.append("holds '{!s}' which is used in room {:d} at the {!s}".format(
                            info['inside']['name'], info['inside']['usable_in'], info['inside']['usable_at']))
                    elif info['inside']['type'] == 'object':
                        attributes.append("will spawn object '{!s}' if being interacted with".format(
                            info['inside']['name']))

                print("* {!s} - {!s}".format(info['name'], ", ".join(attributes)))
            print()

    def save_game(self):
        """
        Save the current game state
        If a file was used loading the game, re-use it
        """
        if self.game_file == None:
            while True:
                user_input = input("Type a filename to save to (will be re-used next time you save: ")

                # The filename must be at least 1 char long
                if user_input == "":
                    print("That's not a good filename...")
                    continue

                # We don't allow the user to overwrite existing files (at all)
                if os.path.isfile(user_input):
                    print("It seems like that file already exists, chose another filename")
                    continue

                with open(user_input, 'w') as f:
                    json.dump(self.game, f, indent=4)

                print("File saved!")
                self.game_file = user_input
                break
        else:
            # Auto save to last saved/loaded file if one exist
            print("Saving to the current game file, {!s}".format(self.game_file))
            with open(self.game_file, 'w') as f:
                json.dump(self.game, f, indent=4)

    def _setup_game(self):
        """
        Setup game state. This method loads the JSON file and converts it to a dictionary
        """
        l = self.game_file if self.game_file != None else 'default.json'

        with open(l, 'r') as f:
            game = json.load(f)

        return game

    def _end_game(self):
        """
        The user completed the game, woho!
        """
        print(self.game['end_text'])

        # Prompt the user to save if they want to so they can continue and explore more
        user_input = input("Would you like to save the game at this completed state? [y/n]: ")
        if user_input in ('y', 'Y'):
            self.save_game()
        else:
            print("Alright, nothing saved. Hope you remember the path!")

        self.game_completed = True
 


