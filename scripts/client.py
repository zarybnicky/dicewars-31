#!/usr/bin/env python3
from argparse import ArgumentParser
import logging
from PyQt5.QtWidgets import QApplication
import sys

import importlib

from dicewars.client.game import Game
from dicewars.client.ui import ClientUI

from utils import get_logging_level


def get_ai_constructor(ai_specification):
    ai_module = importlib.import_module('dicewars.client.ai.ai{}'.format(ai_specification))

    return ai_module.AI


def main():
    """Client side of Dice Wars
    """
    parser = ArgumentParser(prog='Dice_Wars-client')
    parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
    parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
    parser.add_argument('-d', '--debug', help="Enable debug output", default='WARN')
    parser.add_argument('--ai', help="Ai version", type=int)
    args = parser.parse_args()

    log_level = get_logging_level(args)

    logging.basicConfig(level=log_level)
    logger = logging.getLogger('CLIENT')

    game = Game(args.address, args.port)

    if args.ai:
        ai = get_ai_constructor(args.ai)(game)
        ai.run()
    else:
        app = QApplication(sys.argv)
        ui = ClientUI(game)
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
