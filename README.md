# py-adventure
A simple CLI mini game written in Python

```
$ python3 adventure.py --help
Usage: adventure.py

--help     | -h   - Print this help text
--info     | -i   - Print info about the game
--version  | -v   - Print version of the program
--about    | -a   - Print information about the developer
--cheat    | -c   - Print available cheats and tricks
--load     | -l   - Load game from save file
```

## About
This is a text based game where your objective is to find your way through a set of rooms. In each room there are objects laying around which can be interacted with by kicking, opening or moving. Sometimes an opened object might include another object.

Some objects can be picked up and stored in your inventory. You can use items you've picked up by typing ```use [item]```.

To move between rooms you you can type ```forward``` or ```backward```.

## Commands

| Command | Short | Description |
| ------ | ------ | ------ |
| info | i | Print information and help text |
| forward | fr | Go forward to the next room |
| back | ba | Go backwards to previous room | 
| look | se | Look around in the room |
| clue | l | List hints inside the room |
| quit | q | Quit the game |
| save | sp | Save your progress |
| | | |
| object | o | List objects inside the room |
| look | t | Look at ```[object]``` |
| open | | Open ```[object]``` |
| kick | s | Kick ```[object]``` |
| move | f | Move ```[object]``` |
| | | |
| inventory | inv | List your current inventory |
| take | | Take ```[object]``` |
| drop | sl | Drop ```[object]``` |
| use | a | Use ```[object]``` | 

## Customizing
TL;DR: See ```default.json``` for complete game setup with JSON. You can create any game you want and load your custom JSON file.

This whole game is based on a JSON template combined with optional room ASCII which can easily be customized.

The JSON file will include the same information as the save file if the game is saved but at it's default state. You can select any room number to start in if you want the player to be able to move backwards. The layout of the JSON file looks like this:

```python
{
  "game_name": "Name of the game",
  "inventory": {},
  "highest_room_id": 1,
  "current_room_id": 1,
  "start_text": "Text when game is started",
  "end_text": "Text when game is completed",
  "rooms": {
    ...
  }
```
### Rooms
Each room is defined in above mentioned JSON file in in the rooms dict. The room format looks like this:

```python
{
  "1": {
    "number": 1,
    "info": "Short information about the room",
    "objects": {
      ...
    }
  }
}
```

#### Objects
A room can hold multiple objects and each object can hold one additional object. The object format looks like this:

```python
{
  "some_object": {
    "name": "Name of object",
    "desc": "Object description",
    "hint": "Hint about the object if asked",
    "breakable": bool,
    "takeable": bool,
    "openable": bool,
    "moveable": bool,
    "break_event": "Text to show when broken (if can be broken)",
    "inside": {
      "type": "item",
      "name": "Name of item inside object",
      "usable_in": room_id_int,
      "desc": "Description about item inside object",
      "usable_at": "Item to use it at"
    }
    "final_state": {
      "name": "Name to show after interacted with",
      "desc": "Description about object at final state"
    }
  }
}
```

```use_event``` tells what action should trigger an event when interacting with the object. This can be one of ```open``` ```break```, ```continue``` or ```game_cleared```. If the event is ```continue``` this menas that a triggered action allows the user to move to the next room. Obviously action ```game_cleared``` means the action completes the game.

```type``` can be either ```item``` or ```object```. ```item```s can be picked up and used like any other items. ```object```s will spawn new objects that can be interacted with as default objects. If the type is an ```object``` the inside dict must include all the values as an object like ```breakable``` and ```takeable```.

**NOTE**: As of now each *_event has it's own key name in the dict so if ```openable``` is true the text for the event must be in ```open_event```.

### ASCII art
To customize ASCII art for the rooms two methods needs to be implemented, currently in ```room_ascii.py```:

* art() - returning a dictionary mapping room id to raw string
* get_room_art(room_id) - returning a string of the room art
