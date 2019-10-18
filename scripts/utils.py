import os
import sys
from subprocess import Popen
import tempfile

from dicewars.server.game.summary import GameSummary


class BoardDefinition:
    def __init__(self, board, ownership, strength):
        assert(board is None or isinstance(board, int))
        assert(ownership is None or isinstance(ownership, int))
        assert(strength is None or isinstance(strength, int))
        self.board = board
        self.ownership = ownership
        self.strength = strength

    def to_args(self):
        args = []
        if self.board is not None:
            args.extend(['-b', str(self.board)])
        if self.ownership is not None:
            args.extend(['-o', str(self.ownership)])
        if self.strength is not None:
            args.extend(['-s', str(self.strength)])
        return args

    def __str__(self):
        return "board: {}, ownership: {}, strength: {}".format(self.board, self.ownership, self.strength)


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


def get_nickname(ai_spec):
    if ai_spec is not None:
        nick = '{} (AI)'.format(ai_spec)
    else:
        nick = 'Human'

    return nick


def log_file_producer(logdir, process):
    if logdir is None:
        return open(os.devnull, 'w')
    else:
        return open('{}/{}'.format(logdir, process), 'w')


def run_ai_only_game(port, address, process_list, ais, board_definition=None, fixed=None, client_seed=None, logdir=None):
    logs = []
    process_list.clear()

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
    if board_definition is not None:
        server_cmd.extend(board_definition.to_args())
    if fixed is not None:
        server_cmd.extend(['-f', str(fixed)])

    server_output = tempfile.TemporaryFile('w+')
    logs.append(log_file_producer(logdir, 'server.txt'))
    process_list.append(Popen(server_cmd, stdout=server_output, stderr=logs[-1]))

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

        logs.append(log_file_producer(logdir, 'client-{}.log'.format(ai_version)))
        process_list.append(Popen(client_cmd, stderr=logs[-1]))

    for p in process_list:
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


class SingleLineReporter:
    def __init__(self, mute):
        self.last_line_len = 0
        self.mute = mute

    def clean(self):
        if self.mute:
            return

        sys.stdout.write('\r' + ' '*self.last_line_len + ' '*len('^C'))
        sys.stdout.write('\r')

    def report(self, line):
        if self.mute:
            return

        self.clean()
        self.last_line_len = len(line)
        sys.stdout.write(line)
