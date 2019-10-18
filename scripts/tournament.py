#!/usr/bin/env python3
import sys
from signal import signal, SIGCHLD
from argparse import ArgumentParser

from utils import run_ai_only_game, get_nickname, BoardDefinition
import random


parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-n', '--nb-games', help="Number of games.", type=int, default=1)
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('-b', '--board', help="Seed for generating board", type=int)
parser.add_argument('-l', '--logdir', help="Folder to store last running logs in.")
parser.add_argument('-r', '--report', help="State the game number on the stdout", action='store_true')

procs = []


def signal_handler(signum, frame):
    """Handler for SIGCHLD signal that terminates server and clients
    """
    for p in procs:
        try:
            p.kill()
        except ProcessLookupError:
            pass


PLAYING_AIs = [
    'dt.rand',
    'dt.stei',
    'kb.phased',
]
NB_GAMES = 25
UNIVERSAL_SEED = 42

players_info = {ai: [] for ai in PLAYING_AIs}


def get_combatants(nb_players, tournament_summary):
    return random.sample(list(tournament_summary.keys()), nb_players)


class PlayerPerformance:
    def __init__(self, name, games):
        nickname = get_nickname(name)
        self.nb_games = len(games)
        self.nb_wins = sum(game.winner == nickname for game in games)
        self.winrate = self.nb_wins/self.nb_games
        self.name = name

    def __str__(self):
        return '{} {:.2f} % winrate [ {} / {} ]'.format(self.name, 100.0*self.winrate, self.nb_wins, self.nb_games)


def board_definitions(initial_board_seed):
    board_seed = initial_board_seed
    while True:
        yield BoardDefinition(board_seed, UNIVERSAL_SEED, UNIVERSAL_SEED)
        board_seed += 1


def main():
    args = parser.parse_args()

    signal(SIGCHLD, signal_handler)

    games_played = 0
    for board_definition in board_definitions(args.board):
        if games_played == NB_GAMES:
            break
        games_played += 1

        combatants = get_combatants(2, players_info)
        if args.report:
            sys.stdout.write('\r' + ' '*50)
            sys.stdout.write('\r{} {}'.format(games_played, ' vs. '.join(combatants)))
        try:
            game_summary = run_ai_only_game(
                args.port, args.address, procs, combatants,
                board_definition,
                fixed=UNIVERSAL_SEED,
                client_seed=UNIVERSAL_SEED,
                logdir=args.logdir,
            )
            for player in combatants:
                players_info[player].append(game_summary)
        except KeyboardInterrupt:
            for p in procs:
                p.kill()
            break

    if args.report:
        sys.stdout.write('\r')

    performances = [PlayerPerformance(player, games) for player, games in players_info.items()]
    performances.sort(key=lambda perf: perf.winrate, reverse=True)

    for perf in performances:
        print(perf)


if __name__ == '__main__':
    main()
