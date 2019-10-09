#!/usr/bin/env python3
import tempfile
import sys
from signal import signal, SIGCHLD
from subprocess import Popen
from time import sleep
from argparse import ArgumentParser

from dicewars.server.game.summary import GameSummary
from dicewars.server.game.summary import get_win_rates


parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-n', '--nb-games', help="Number of games.", type=int, default=1)
parser.add_argument('-p', '--port', help="Server port", type=int, default=5005)
parser.add_argument('-a', '--address', help="Server address", default='127.0.0.1')
parser.add_argument('--ai', help="Specify AI versions as a sequence of ints.",
                    type=int, nargs='+')

procs = []


def signal_handler(signum, frame):
    """Handler for SIGCHLD signal that terminates server and clients
    """
    for p in procs:
        try:
            p.kill()
        except ProcessLookupError:
            pass


def run_single_game(args):
    server_cmd = [
        "./scripts/server.py",
        "-n", str(len(args.ai)),
        "-p", str(args.port),
        "-a", str(args.address),
    ]

    server_output = tempfile.TemporaryFile('w+')
    procs.append(Popen(server_cmd, stdout=server_output))

    for ai_version in args.ai:
        client_cmd = [
            "./scripts/client.py",
            "-p", str(args.port),
            "-a", str(args.address),
            "--ai", str(ai_version),
        ]

        procs.append(Popen(client_cmd))
        sleep(0.1)

    for p in procs:
        p.wait()

    server_output.seek(0)
    game_summary = GameSummary.from_repr(server_output.read())
    return game_summary


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
        try:
            game_summary = run_single_game(args)
            summaries.append(game_summary)
        except KeyboardInterrupt:
            for p in procs:
                p.kill()

    win_numbers = get_win_rates(summaries, len(args.ai))
    sys.stdout.write("Win counts {}\n".format(win_numbers))


if __name__ == '__main__':
    main()
