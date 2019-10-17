#!/usr/bin/env python3
import tempfile
import sys
from signal import signal, SIGCHLD
from subprocess import Popen
from argparse import ArgumentParser

from dicewars.server.game.summary import GameSummary
from dicewars.server.game.summary import get_win_rates

from utils import get_nickname


parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-n', '--nb-games', help="Number of games.", type=int, default=1)
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('-b', '--board', help="Seed for generating board", type=int)
parser.add_argument('-s', '--strength', help="Seed for dice assignment", type=int)
parser.add_argument('-o', '--ownership', help="Seed for province assignment", type=int)
parser.add_argument('-f', '--fixed', help="Random seed to be used for player order and dice rolls", type=int)
parser.add_argument('-c', '--client-seed', help="Seed for clients", type=int)
parser.add_argument('--ai', help="Specify AI versions as a sequence of ints.", nargs='+')
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


def run_single_game(port, address, ais, board=None, ownership=None, strength=None, fixed=None, client_seed=None):
    logs = []
    procs.clear()

    ai_nicks = [get_nickname(ai) for ai in ais]

    server_cmd = [
        "./scripts/server.py",
        "-n", str(len(ais)),
        "-p", str(port),
        "-a", str(address),
        '--debug', 'DEBUG',
    ]
    server_cmd.append('-r')
    server_cmd.extend(ai_nicks)
    if board is not None:
        server_cmd.extend(['-b', str(board)])
    if ownership is not None:
        server_cmd.extend(['-o', str(ownership)])
    if strength is not None:
        server_cmd.extend(['-s', str(strength)])
    if fixed is not None:
        server_cmd.extend(['-f', str(fixed)])

    server_output = tempfile.TemporaryFile('w+')
    logs.append(open('server.log', 'w'))
    procs.append(Popen(server_cmd, stdout=server_output, stderr=logs[-1]))

    for ai_version in ais:
        client_cmd = [
            "./scripts/client.py",
            "-p", str(port),
            "-a", str(address),
            "--ai", str(ai_version),
            '--debug', 'DEBUG',
        ]
        if client_seed is not None:
            client_cmd.extend(['-s', str(client_seed)])

        logs.append(open('client-{}.log'.format(ai_version), 'w'))
        procs.append(Popen(client_cmd, stderr=logs[-1]))

    for p in procs:
        p.wait()

    for log in logs:
        log.close()

    server_output.seek(0)
    game_summary = GameSummary.from_repr(server_output.read())
    return game_summary


class ListStats:
    def __init__(self, the_list):
        self.min = min(the_list)
        self.avg = sum(the_list)/len(the_list)
        self.max = max(the_list)

    def __str__(self):
        return 'min/avg/max {}/{:.2f}/{}'.format(self.min, self.avg, self.max)


def main():
    """
    Run the Dice Wars game among AI's.

    Example:
        ./dicewars.py --nb-games 16 --ai 4 4 2 1
        # runs 16 games four-player games with AIs 4 (two players), 2, and 1
    """
    args = parser.parse_args()

    signal(SIGCHLD, signal_handler)

    if len(args.ai) < 2 or len(args.ai) > 8:
        print("Unsupported number of AIs")
        exit(1)

    summaries = []
    for i in range(args.nb_games):
        if args.report:
            sys.stdout.write('\r{}'.format(i))
        try:
            board_seed = None if args.board is None else args.board + i
            game_summary = run_single_game(
                args.port, args.address, args.ai,
                board=board_seed,
                ownership=args.ownership,
                strength=args.strength,
                fixed=args.fixed,
                client_seed=args.client_seed,
            )
            summaries.append(game_summary)
        except KeyboardInterrupt:
            for p in procs:
                p.kill()
            break
        except AttributeError:
            for p in procs:
                p.kill()
    if args.report:
        sys.stdout.write('\r')

    win_numbers = get_win_rates(summaries, len(args.ai))
    sys.stdout.write("Win counts {}\n".format(win_numbers))

    nb_battles_stats = ListStats([s.nb_battles for s in summaries])
    sys.stdout.write("Nb battles {}\n".format(nb_battles_stats))


if __name__ == '__main__':
    main()
