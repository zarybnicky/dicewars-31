#!/usr/bin/env python3

from argparse import ArgumentParser
import logging

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


def main():
    """
    Server for Dice Wars
    """

    parser = ArgumentParser(prog='Dice_Wars-server')
    parser.add_argument('-n', '--number-of-players', help="Number of players", type=int, default=2)
    parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
    parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
    parser.add_argument('-d', '--debug', help="Enable debug output", default='WARN')
    args = parser.parse_args()
    log_level = get_logging_level(args)

    logging.basicConfig(level=log_level)
    logger = logging.getLogger('SERVER')
    logger.debug("Command line arguments: {0}".format(args))

    game = Game(args.number_of_players, args.address, args.port)
    game.run()


if __name__ == '__main__':
    main()
