# Dice Wars

Dice Wars is a strategy game where players take turns to attack adjacent territories to expand
their area. Each territory contains a number of dice determining player's presence
and strength. The objective of the game is to conquer all territories and thus eliminate each opponent.

This is a client-server implementation that was created as a part of a [bachelor's thesis at FIT BUT](https://www.vutbr.cz/www_base/zav_prace_soubor_verejne.php?file_id=180901)
where it is described in more detail.


## Installation

To use this, you need to have python3 and the following python packages:

    hexutil
    numpy
    pyqt

A standard ``requirements.txt`` is provided.

Furthermore, the root of the repository needs to be in ``PYTHONPATH``.

## Running the game

There are three different scripts prepared, which allow for testing different scenarios.
However, they all expose a common set of parameters for controlling the pseudo-randomness in the game:

    -b  geometry of the board
    -o  clustering of areas into possesion of individual players  
    -s  assignment of dice to areas

When not set, the source of pseudo-random numbers is seeded from current time, becoming effectively random.

Additionally, client-server communication can be controlled by:

    -p    port, default 5005
    -a    address, default is localhost

Finally, individual AIs are refered to as follows:
For every ``module`` in ``dicewars.ai``, which contains a class ``AI``, the ``AI`` is identified by ``module``. Examples are fiven throughout the following sections.

### Playing with human
Starts a human-controlled client along those driven by AIs.

    ./scripts/dicewars-human.py --ai dt.stei dt.rand xlogin42

### Playing with fixed AI order
Starts a set of games between AIs in given order.
Increments the board seed with every game.
Additionally exposes these options:

    -n      number of board to be played
    -l      folder where to put logs of last game
    -r      keep reporting which game is being played

An example:

    ./scripts/dicewars-ai-only.py -r -b 11 -o 22 -s 33 -c 44 -n 10 -l ../logs --ai dt.stei xlogin42

### Running a tournament
Keeps picking a subset of AIs of specified size and has them play together.
The total set of AIs considered is given in the script itself.
Additionally exposes these options:

    -n      number of board to be played
    -g      size of games in number of players
    -l      folder where to put logs of last game
    -r      keep reporting what game is being played
    --save  where to save the resulting list of games

For every board, all permutations of player order are played, thus the total number of games equals ``N x G!``

## Implementing AIs
See ``dicewars/ai/template.py`` and other existing AIs in the package.
An AI is a class implementing two standard functions: ``__init__()`` and ``ai_turn()``

### Name vs. instance
Players and areas exist primary as instances of Player and Area.
However -- originally for serialization purposes -- they are both referred to by their "name".
These names are instances of `int`.
Board can return Areas as given by name` every Area kwons its name.

There is no reason for an AI to access instances of Player.

## AI interface

The constructor is expected to takes following parameters:

    player_name     the name of the player this AI will control
    board           an instance of ``dicewars.client.game.Board``
    players_order   in what order do players take turns

The turn making method is expected to takes following parameters:

    board               an instance of ``dicewars.client.game.Board``   
    nb_moves_this_turn  number of attacks made in this turn
    nb_turns_this_game  number of turns ended so far
    previous_time_left  time (in seconds) left after last decision making

The ``AI.ai_turn()`` is required to return an instance of ``BattleCommand`` or ``EndTurnCommand``.

Multi-module implementation is possible, see ``xlogin42`` for an example.

## Learning about the world
Board's ``get_player_areas()``, ``get_player_border()``, and ``get_players_regions()`` can be used to discover areas belonging to any player in the game.
Instances of ``Area`` then allow inquiry through ``get_adjacent_areas()``, ``get_owner_name()`` and ``get_dice()``.

It may also be practical to acquire all possible moves from ``dicewars.ai.utils.possible_attacks()``.
This module also provides formulas for probability of conquering and holding an Area.

The instance of ``Board`` passed to AI is a deepcopy, so the AI is free to mangle it in any way it deemed useful.
