#!/usr/bin/env python3
from signal import signal, SIGCHLD
from argparse import ArgumentParser

import math
import numpy as np
import itertools
from utils import run_ai_only_game, get_nickname, BoardDefinition, SingleLineReporter
import random
import pickle


parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('-b', '--board', help="Seed for generating board", type=int)
parser.add_argument('-n', '--nb-boards', help="How many boards should be played", type=int, required=True)
parser.add_argument('-g', '--game-size', help="How many players should play a game", type=int, required=True)
parser.add_argument('-s', '--seed', help="Seed sampling players for a game", type=int)
parser.add_argument('-l', '--logdir', help="Folder to store last running logs in.")
parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-r', '--report', help="State the game number on the stdout", action='store_true')
parser.add_argument('--save', help="Where to put pickled GameSummaries")
parser.add_argument('--load', help="Which GameSummaries to start from")

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
    'dt.sdc',
    'dt.ste',
    'dt.stei',
    'dt.wpm_d',
    'dt.wpm_s',
    'dt.wpm_c',
    'xlogin42',
    'xlogin00',
]
UNIVERSAL_SEED = 42

players_info = {ai: {'games': []} for ai in PLAYING_AIs}


class CombatantsProvider:
    def __init__(self, players):
        self.game_numbers = np.zeros((len(players), len(players)), dtype=np.int)
        self.players = players

    def get_combatants_equalizing(self, nb_combatants):
        per_player_count = {ai: nb_games for ai, nb_games in zip(self.players, np.sum(self.game_numbers, axis=1))}

        pivot_ind = self.players.index(sorted(per_player_count, key=lambda p: per_player_count[p])[0])
        possible_competitors = [self.players.index(ai) for ai in self.players if self.players.index(ai) != pivot_ind]
        competitors = sorted(possible_competitors, key=lambda p: (self.game_numbers[pivot_ind][p], per_player_count[self.players[p]]))[:nb_combatants-1]

        players = [pivot_ind] + competitors

        for a_ind in players:
            for b_ind in players:
                self.game_numbers[a_ind][b_ind] += nb_combatants

        return [self.players[p] for p in players]


provider = CombatantsProvider(PLAYING_AIs)
get_combatants = provider.get_combatants_equalizing


class PlayerPerformance:
    def __init__(self, name, games):
        nickname = get_nickname(name)
        self.nb_games = len(games)
        self.nb_wins = sum(game.winner == nickname for game in games)
        if self.nb_games > 0:
            self.winrate = self.nb_wins/self.nb_games
        else:
            self.winrate = float('nan')
        self.name = name

        self.per_competitor_winrate = {}
        for competitor in PLAYING_AIs:
            his_games = [game for game in games if get_nickname(competitor) in game.participants()]
            if his_games:
                self.per_competitor_winrate[competitor] = (sum(game.winner == nickname for game in his_games)/len(his_games), len(his_games))
            else:
                self.per_competitor_winrate[competitor] = (float('nan'), len(his_games))

    def __str__(self):
        per_competitor_str = ' '.join('{:.1f}/{}'.format(100.0*winrate[0], winrate[1]) for ai, winrate in self.per_competitor_winrate.items())
        return '{} {:.2f} % winrate [ {} / {} ] {}'.format(self.name, 100.0*self.winrate, self.nb_wins, self.nb_games, per_competitor_str)

    def competitors_header(self):
        return '{} {} % winrate [ {} / {} ] {}'.format('.', '.', '.', '.', ' '.join(str(ai) for ai in PLAYING_AIs))


def board_definitions(initial_board_seed):
    board_seed = initial_board_seed
    while True:
        yield BoardDefinition(board_seed, UNIVERSAL_SEED, UNIVERSAL_SEED)
        board_seed += 1


def main():
    args = parser.parse_args()
    random.seed(args.seed)

    signal(SIGCHLD, signal_handler)

    if args.load:
        with open(args.load, 'rb') as f:
            all_games = pickle.load(f)
    else:
        all_games = []

    boards_played = 0
    reporter = SingleLineReporter(not args.report)
    try:
        for board_definition in board_definitions(args.board):
            if boards_played == args.nb_boards:
                break
            boards_played += 1

            combatants = get_combatants(args.game_size)
            nb_permutations = math.factorial(len(combatants))
            for i, permuted_combatants in enumerate(itertools.permutations(combatants)):
                reporter.report('\r{} {}/{} {}'.format(boards_played, i+1, nb_permutations, ' vs. '.join(permuted_combatants)))
                game_summary = run_ai_only_game(
                    args.port, args.address, procs, permuted_combatants,
                    board_definition,
                    fixed=UNIVERSAL_SEED,
                    client_seed=UNIVERSAL_SEED,
                    logdir=args.logdir,
                    debug=args.debug,
                )
                all_games.append(game_summary)
    except KeyboardInterrupt:
        for p in procs:
            p.kill()

    reporter.clean()

    if args.save:
        with open(args.save, 'wb') as f:
            pickle.dump(all_games, f)

    for game in all_games:
        participants = game.participants()
        for player in players_info:
            if get_nickname(player) in participants:
                players_info[player]['games'].append(game)

    performances = [PlayerPerformance(player, info['games']) for player, info in players_info.items()]
    performances.sort(key=lambda perf: perf.winrate, reverse=True)

    perf_strings = [performances[0].competitors_header()] + [str(perf) for perf in performances]
    fields = [perf.split() for perf in perf_strings]

    print(column_t(fields))


def column_t(items):
    for line in items:
        assert(len(line) == len(items[0]))

    col_widths = []
    for col_id in range(len(items[0])):
        col_widths.append(max(len(line[col_id]) for line in items))

    formatted_lines = []
    for line in items:
        fmts = ['{{: <{}}}'.format(width) for width in col_widths]
        line_fmt = '{}\n'.format(' '.join(fmts))
        formatted_lines.append(line_fmt.format(*line))

    return ''.join(formatted_lines)


if __name__ == '__main__':
    main()
