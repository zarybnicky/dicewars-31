#!/usr/bin/env python3
import tempfile
import sys
from signal import signal, SIGCHLD
from subprocess import Popen
from time import sleep
from argparse import ArgumentParser
from server.game.summary import GameSummary


parser = ArgumentParser(prog='Dice_Wars')
parser.add_argument('-n', '--number-of-players', help="Number of players.", type=int, default=2)
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


def main():
    """
    Run the Dice Wars game among AI's.

    Example:
        ./dicewars.py -n 4 --ai 4 2 1
        # runs a four-player game with AIs 4, 2, and 1
    """
    args = parser.parse_args()

    signal(SIGCHLD, signal_handler)

    if len(args.ai) != args.number_of_players:
        print("Non-matching number of AIs")
        exit(1)

    try:
        server_cmd = [
            "./server/server.py",
            "-n", str(args.number_of_players),
            "-p", str(args.port),
            "-a", str(args.address),
        ]

        server_output = tempfile.TemporaryFile('w+')
        procs.append(Popen(server_cmd, stdout=server_output))

        for ai_version in args.ai:
            client_cmd = [
                "./client/client.py",
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
        sys.stdout.write("{}".format(game_summary))

    except KeyboardInterrupt:
        for p in procs:
            p.kill()


if __name__ == '__main__':
    main()
