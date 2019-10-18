from random import shuffle, uniform
import time

from ..ai_base import GenericAI
from ..utils import possible_attacks


class AI(GenericAI):
    """Naive player agent

    This agent performs all possible moves in random order
    """

    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game
        """
        super(AI, self).__init__(game)

    def ai_turn(self):
        """AI agent's turn

        Get a random area. If it has a possible move, the agent will do it.
        If there are no more moves, the agent ends its turn.
        """
        if self.moves_this_turn == 2:
            self.logger.debug("I'm too well behaved. Let others play now.")
            self.send_message('end_turn')

            return True

        attacks = list(possible_attacks(self.board, self.player_name))
        shuffle(attacks)
        for source, target in attacks:
            nap_len = uniform(0.0, 1.5)
            self.logger.debug("Taking a nap of {} secs".format(nap_len))
            time.sleep(nap_len)

            self.send_message('battle', attacker=source.get_name(), defender=target.get_name())
            return True

        self.logger.debug("No more possible turns.")
        self.send_message('end_turn')

        return True
