import logging
import torch
import torch.nn as nn
from os.path import dirname

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand
from ..utils import possible_attacks
from .utils import get_features_client

class AI:
    def __init__(self, player_name, board, players_order):
        self.player_name = player_name
        self.logger = logging.getLogger('AI')
        self.model = nn.Sequential(
            nn.Linear(21, 13),
            nn.PReLU(),
            nn.Linear(13, 8),
            nn.PReLU(),
            nn.Linear(8, 2),
            nn.Sigmoid(),
        )
        self.model.load_state_dict(torch.load(dirname(__file__) + '/local-predictor.model'))
        self.model.eval()

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        attacks = list(
            (self.model(torch.tensor(
                get_features_client(board, attack[0].get_name(), attack[1].get_name())[0]
            )), attack)
            for attack in possible_attacks(board, self.player_name)
        )
        # for a in attacks:
        #     print(a[0], get_features_client(board, a[1][0].get_name(), a[1][1].get_name())[0])
        # P(hold source) > 50%
        attacks = filter(lambda x: x[0][0] > .4 and x[0][1] > .4, attacks)
        # sort by P(hold target)
        attacks = sorted(attacks, key=lambda x: x[0][0] ** 2 * x[0][1], reverse=True)

        if attacks:
            attack = attacks[0]
            # print('Win', attack[0][0].item(), attack[0][1].item())
            return BattleCommand(attack[1][0].get_name(), attack[1][1].get_name())
        return EndTurnCommand()
