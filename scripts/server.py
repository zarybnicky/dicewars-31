#!/usr/bin/env python3

from argparse import ArgumentParser
import logging
import random

from itertools import cycle

from dicewars.server.game import Board, BoardGenerator
from dicewars.server.game import Game


def get_logging_level(args):
    """
    Parse command-line arguments.
    """
    if args.debug.lower() == 'debug':
        logging = 10
    elif args.debug.lower() == 'info':
        logging = 20
    elif args.debug.lower() == 'error':
        logging = 40
    else:
        logging = 30

    return logging


def area_player_mapping(nb_players, nb_areas):
    assignment = {}
    unassigned_areas = list(range(1, nb_areas+1))
    player_cycle = cycle(range(1, nb_players+1))

    while unassigned_areas:
        player_no = next(player_cycle)
        area_no = random.choice(unassigned_areas)
        assignment[area_no] = player_no
        unassigned_areas.remove(area_no)

    return assignment


def main():
    """
    Server for Dice Wars
    """

    parser = ArgumentParser(prog='Dice_Wars-server')
    parser.add_argument('-n', '--number-of-players', help="Number of players", type=int, default=2)
    parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
    parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
    parser.add_argument('-d', '--debug', help="Enable debug output", default='WARN')
    parser.add_argument('-b', '--board', help="Random seed to be used for board creating", type=int)
    parser.add_argument('-o', '--ownership', help="Random seed to be used for province assignment", type=int)
    args = parser.parse_args()
    log_level = get_logging_level(args)

    logging.basicConfig(level=log_level)
    logger = logging.getLogger('SERVER')
    logger.debug("Command line arguments: {0}".format(args))

    random.seed(args.board)
    generator = BoardGenerator()
    board = Board(generator.generate_board())

    random.seed(args.ownership)
    area_ownership = area_player_mapping(args.number_of_players, board.get_number_of_areas())

    game = Game(board, area_ownership, args.number_of_players, args.address, args.port)
    game.run()


if __name__ == '__main__':
    main()
