from ..ai_base import GenericAI
from ..utils import possible_attacks


class AI(GenericAI):
    """Agent using Strength Difference Checking (SDC) strategy

    This agent prefers moves with highest strength difference
    and doesn't make moves against areas with higher strength.
    """
    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game

        Attributes
        ----------
        possible_attackers : list of int
            Areas that can make an attack
        attacks_done : list of int
        """
        super(AI, self).__init__(game)
        self.possible_attackers = []
        self.attacks_done = []

    def ai_turn(self):
        """AI agent's turn

        Creates a list with all possible moves along with associated strength
        difference. The list is then sorted in descending order with respect to
        the SD. A move with the highest SD is then made unless the highest
        SD is lower than zero - in this case, the agent ends its turn.
        """

        attacks = []
        for source, target in possible_attacks(self.board, self.player_name):
            area_dice = source.get_dice()
            strength_difference = area_dice - target.get_dice()
            attack = [source.get_name(), target.get_name(), strength_difference]
            attacks.append(attack)

        attacks = sorted(attacks, key=lambda attack: attack[2], reverse=True)

        if attacks and attacks[0][2] >= 0:
            self.send_message('battle', attacks[0][0], attacks[0][1])
            return True

        self.send_message('end_turn')

        return True
