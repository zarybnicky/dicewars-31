import logging

from .area import Area


class Board(object):
    """Game board
    """
    def __init__(self, areas, board):
        """
        Parameters
        ----------
        areas : dict of int: list of int
            Dictionary of game areas and their neighbours
        board : dict
            Dictionary describing the game's board
        """
        self.logger = logging.getLogger('CLIENT')
        self.areas = {}
        for area in areas:
            self.areas[area] = Area(area, areas[area]['owner'], areas[area]['dice'],
                                    board[area]['neighbours'], board[area]['hexes'])

    def get_area(self, idx):
        """Get Area given its name
        """
        return self.areas[str(idx)]

    def get_player_areas(self, player):
        return [area for area in self.areas.values() if area.get_owner_name == player]

    def get_player_dice(self, player):
        """Get all dice of a single player
        """
        return sum([area.dice() for area in self.get_player_areas(player)])
