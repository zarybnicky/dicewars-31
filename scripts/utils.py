import tempfile
from subprocess import Popen
from dicewars.server.game.summary import GameSummary


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


def run_ai_only_game(port, address, process_list, ais, board=None, ownership=None, strength=None, fixed=None, client_seed=None):
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

        logs.append(open('client-{}.log'.format(ai_version), 'w'))
        process_list.append(Popen(client_cmd, stderr=logs[-1]))

    for p in process_list:
        p.wait()

    for log in logs:
        log.close()

    server_output.seek(0)
    game_summary = GameSummary.from_repr(server_output.read())
    return game_summary
