import pickle
from queue import Queue
from .player import Player


class StaticGame(object):
    """Represantation of the game state
    """
    def __init__(self, f):
        self.input_queue = Queue()
        self.players = {}

        save_game = pickle.load(f)

        print(save_game['player_name'])
        print(save_game['order'])

        self.player_name = save_game['player_name']
        self.board = save_game['board']
        self.current_player_name = save_game['current_player_name']
        self.players_order = save_game['order']

        self.players = {i: Player(i, -1) for i in self.players_order}

        self.current_player = self.players[self.current_player_name]

        print("This is player name {}, the players order is {}".format(self.player_name, self.players_order))
