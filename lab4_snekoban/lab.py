"""
6.1010 Lab 4:
Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def remove_from_game_rep(game, obj, row, col):
    """
    INPUT: game (dict of frozensets), obj (str), row (int), col (int)
    OUTPUT: None
    Edits game to remove (row, col) from the frozenset keyed to obj.
    """
    game[obj] = game[obj] ^ frozenset({(row, col)})

def add_to_game_rep(game, obj, row, col):
    """
    INPUT: game (dict of frozensets), obj (str), row (int), col (int)
    OUTPUT: None
    Edits game to add obj to the game, where obj is the key and
    (row, col) is in obj's frozenset.
    """
    if obj in game:
        game[obj] = game[obj] ^ frozenset({(row, col)})
    else:
        game[obj] = frozenset({(row, col)})

def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    I will represent the game as a dictionary where the keys are the types of
    objects ("wall", "computer", "player", "target"), while the values are
    frozensets of the locations of the objects in question.
    """
    game_rep = {}
    for row, row_content in enumerate(level_description):
        for col, objects in enumerate(row_content):
            for obj in objects:
                add_to_game_rep(game_rep, obj, row, col)
    return game_rep

def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    if "target" not in game:
        return False

    return not game["target"] ^ game["computer"]

def get_objs_at_loc(game, row, col):
    """
    INPUT: game (dict of frozensets), row (int), col (int)
    OUTPUT: occupants (list)
    occupants is a list of all objects at the given location (row, col)
    """
    occupants = []
    for obj in game:
        for (r, c) in game[obj]:
            if (r, c) == (row, col):
                occupants.append(obj)
    return occupants

def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a new game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    # this is too complezx helper funcs
    new_game = game.copy()
    player_loc = list(game["player"])[0]
    d_vect = direction_vector[direction]
    new_loc = tuple(map(sum, zip(player_loc, d_vect)))
    if ("computer" in game) and (new_loc in game["computer"]):
        blocking_loc = tuple(map(sum, zip(new_loc, d_vect)))
        if not ((blocking_loc in game["wall"]) or (blocking_loc in game["computer"])):
            # the player is able to push the computer
            remove_from_game_rep(new_game, "computer", *new_loc)
            add_to_game_rep(new_game, "computer", *blocking_loc)
            new_game["player"] = frozenset({new_loc})
    elif not new_loc in game["wall"]:
        # in this case, there's nothing blocking the player
        new_game["player"] = frozenset({new_loc})
    return new_game

def get_dimensions(game):
    height, width = 0, 0
    for obj in game:
        for (row, col) in game[obj]:
            if row >= height:
                height = row + 1
            if col >= width:
                width = col + 1
    return height, width

def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    height, width = get_dimensions(game)

    canon_rep = [[[] for _ in range(width)] for _ in range(height)]

    for obj in game:
        for (row, col) in game[obj]:
            canon_rep[row][col].append(obj)

    return canon_rep

def game_rep_to_solve_rep(game_rep):
    """
    INPUT: game (dict of frozensets)
    OUTPUT: solve_rep (tuple (player locations, computer locations))
    """
    return (game_rep["player"], game_rep["computer"])

def solve_rep_to_game_rep(game, solve_rep):
    """
    INPUT: game (dict of frozensets, keys = "player", "computer", "wall"), 
           solve_rep (tuple (player locations, computer locations))
    OUTPUT: current_game (dict of frozensets)
    """
    current_game = {
        "player": solve_rep[0],
        "computer": solve_rep[1],
        "wall": game["wall"],
        "target": game["target"]
    }
    current_game["wall"] = game["wall"]
    return current_game

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    # init_movable is a dict of the positions of the player and the computers,
    # since those are the only movable items in the game and thus the only
    # things that need to be stored.
    movable = game_rep_to_solve_rep(game)
    visited = {movable} # set of all visited games
    work_queue = [(movable, ())] # set of paths

    if victory_check(game):
        return []

    while work_queue:
        temp_queue = []
        for temp_movable, path in work_queue:
            temp_game = solve_rep_to_game_rep(game, temp_movable)
            for direction in ["up", "down", "left", "right"]:
                new_game = step_game(temp_game, direction)
                new_path = path + (direction,)
                if victory_check(new_game):
                    return list(new_path)

                new_movable = game_rep_to_solve_rep(new_game)
                if new_movable not in visited:
                    visited.add(new_movable)
                    temp_queue.append((new_movable, new_path))
        work_queue = temp_queue
    return None

if __name__ == "__main__":
    with open("puzzles/t_001.json", "rb") as f:
        test_game = json.load(f)

    test_game_rep = make_new_game(test_game)
    # print(step_game(test_game_rep, "down"))
    print(solve_puzzle(test_game_rep))
    # print(test_game_rep)
    # print(dump_game(test_game_rep))
    # print(test_game == dump_game(test_game_rep))
