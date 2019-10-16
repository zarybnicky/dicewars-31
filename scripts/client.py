#!/usr/bin/env python3
from argparse import ArgumentParser
import logging
from PyQt5.QtWidgets import QApplication
import sys
import random
import json

import importlib

from dicewars.client.game import Game
from dicewars.client.ui import ClientUI

from utils import get_logging_level


def get_ai_constructor(ai_specification):
    ai_module = importlib.import_module('dicewars.client.ai.{}'.format(ai_specification))

    return ai_module.AI


def get_nickname(ai_spec):
    if ai_spec is not None:
        nick = '{} (AI)'.format(ai_spec)
    else:
        nick = 'Human'

    return nick


def main():
    """Client side of Dice Wars
    """
    parser = ArgumentParser(prog='Dice_Wars-client')
    parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
    parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
    parser.add_argument('-d', '--debug', help="Enable debug output", default='WARN')
    parser.add_argument('-s', '--seed', help="Random seed for a client", type=int)
    parser.add_argument('--ai', help="Ai version")
    args = parser.parse_args()

    random.seed(args.seed)

    log_level = get_logging_level(args)

    logging.basicConfig(level=log_level)
    logger = logging.getLogger('CLIENT')

    game = Game(args.address, args.port)
    msg = {
        'type': 'client_desc',
        'nickname': get_nickname(args.ai),
    }
    try:
        game.socket.send(str.encode(json.dumps(msg)))
    except BrokenPipeError:
        logger.error("Connection to server broken.")
        exit(1)

    if args.ai:
        ai = get_ai_constructor(args.ai)(game)
        ai.run()
    else:
        app = QApplication(sys.argv)
        ui = ClientUI(game)
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
