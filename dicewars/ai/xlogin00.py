import random

from dicewars.ai.ai_base import GenericAI
from dicewars.ai.utils import possible_attacks

from dicewars.ai.ai_base import BattleCommand, EndTurnCommand


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
            return EndTurnCommand()

        attacks = list(possible_attacks(self.board, self.player_name))
        if attacks:
            source, target = random.choice(attacks)
            return BattleCommand(source.get_name(), target.get_name())
        else:
            self.logger.debug("No more possible turns.")
            return EndTurnCommand()
