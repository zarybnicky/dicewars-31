import random

from ..ai_base import GenericAI
from ..utils import possible_attacks
from .utils import best_sdc_attack, is_acceptable_sdc_attack

from dicewars.ai.ai_base import BattleCommand, EndTurnCommand


class FinalAI(GenericAI):
    """Naive player agent

    This agent performs all possible moves in random order
    """

    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game
        """
        super().__init__(game)

    def ai_turn(self):
        """AI agent's turn

        Get a random area. If it has a possible move, the agent will do it.
        If there are no more moves, the agent ends its turn.
        """
        if self.turns_finished < 3:
            self.logger.debug("Doing a random move")
            attack_filter = lambda x: x
            attack_selector = random.choice
            attack_acceptor = lambda x: True
        else:
            self.logger.debug("Doing a serious move")
            attack_filter = lambda x: self.from_largest_region(x)
            attack_selector = best_sdc_attack
            attack_acceptor = lambda x: is_acceptable_sdc_attack(x)

        all_moves = list(possible_attacks(self.board, self.player_name))
        if not all_moves:
            self.logger.debug("There are no moves possible at all")
            return EndTurnCommand()

        moves_of_interest = attack_filter(all_moves)
        if not moves_of_interest:
            self.logger.debug("There are no moves of interest")
            return EndTurnCommand()

        the_move = attack_selector(moves_of_interest)

        if attack_acceptor(the_move):
            return BattleCommand(the_move[0].get_name(), the_move[1].get_name())
        else:
            self.logger.debug("The move {} is not acceptable, ending turn".format(the_move))
            return EndTurnCommand()

    def from_largest_region(self, attacks):
        players_regions = self.board.get_players_regions(self.player_name)
        max_region_size = max(len(region) for region in players_regions)
        max_sized_regions = [region for region in players_regions if len(region) == max_region_size]

        the_largest_region = max_sized_regions[0]
        self.logger.debug('The largest region: {}'.format(the_largest_region))
        return [attack for attack in attacks if attack[0].get_name() in the_largest_region]
