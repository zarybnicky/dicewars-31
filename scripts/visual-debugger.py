#!/usr/bin/env python3
import argparse
from PyQt5.QtWidgets import QApplication
import sys

import importlib

from dicewars.client.game.static_game import StaticGame
from dicewars.client.ui import ClientUI
from dicewars.client.ai_driver import AIDriver

from utils import get_logging_level, get_nickname


def get_ai_constructor(ai_specification):
    ai_module = importlib.import_module('dicewars.ai.{}'.format(ai_specification))

    return ai_module.AI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('savegame')
    args = parser.parse_args()

    with open(args.savegame, 'rb') as f:
        game = StaticGame(f)

    app = QApplication(sys.argv)
    ui = ClientUI(game)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
