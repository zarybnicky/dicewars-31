import random

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
        if self.turns_finished < 3:
            self.logger.debug("Doing a random move")
            did_attack = self.random_move()
        else:
            self.logger.debug("Doing a serious move")
            did_attack = self.score_inc_move()

        if not did_attack:
            self.logger.debug("No more possible turns.")
            self.send_message('end_turn')
            self.waitingForResponse = True

        return True

    def random_move(self):
        attacks = list(possible_attacks(self.board, self.player_name))
        if not attacks:
            return False

        source, target = random.choice(attacks)

        self.send_message('battle', attacker=source.get_name(), defender=target.get_name())
        self.waitingForResponse = True
        return True

    def score_inc_move(self):
        players_regions = self.board.get_players_regions(self.player_name)
        max_region_size = max(len(region) for region in players_regions)
        max_sized_regions = [region for region in players_regions if len(region) == max_region_size]

        the_largest_region = max_sized_regions[0]
        self.logger.debug('The largest region: {}'.format(the_largest_region))

        attacks = list(possible_attacks(self.board, self.player_name))
        self.logger.debug('All attacks available: {}'.format([(attack[0].get_name(), attack[1].get_name(), attack[0].get_dice(), attack[1].get_dice()) for attack in attacks]))
        attacks = [attack for attack in attacks if attack[0].get_name() in the_largest_region]
        self.logger.debug('Expanding attacks available: {}'.format([(attack[0].get_name(), attack[1].get_name(), attack[0].get_dice(), attack[1].get_dice()) for attack in attacks]))
        if not attacks:
            return False

        scored_attacks = [(source, target, attacker_advantage(source, target)) for source, target in attacks]
        scored_attacks.sort(key=lambda attack: attack[2], reverse=True)

        source, target, advantage = scored_attacks[0]
        if advantage > 0 or source.get_dice() == 8:
            self.send_message('battle', attacker=source.get_name(), defender=target.get_name())
            self.waitingForResponse = True
            return True
        else:
            return False


def attacker_advantage(attacker, defender):
    return attacker.get_dice() - defender.get_dice()
