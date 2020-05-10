from os.path import dirname

from dicewars.server.game.game import Game
from dicewars.ai.xzaryb00.utils import get_features

class RecordingGame(Game):
    def __init__(self, board, area_ownership, players, addr, port, nicknames_order):
        super().__init__(board, area_ownership, players, addr, port, nicknames_order)
        self.attacks = {}
        self.handle = open(dirname(__file__) + '/turns.csv', 'a')
        self.turn_counter = 0

    def run(self):
        super().run()
        self.turn_counter += len(self.players_order) * 4
        self.flush_attacks()

    def attack(self, atk_name, def_name):
        features = get_features(self.board, atk_name, def_name)
        self.attacks.setdefault(self.turn_counter + len(self.players_order), []).append(features)

    def flush_attacks(self):
        new_attacks = {}
        for target_turn, attacks in self.attacks.items():
            for a in attacks:
                # If the attacker held the atk/def areas in prev turns but holds
                # them no longer, then flip output values to zero
                if a[1][0] and a[2][0] != a[2][1].owner_name:
                    a[1][0] = 0
                if a[1][1] and a[2][0] != a[2][2].owner_name:
                    a[1][1] = 0
            if target_turn <= self.turn_counter:
                for a in attacks:
                    self.handle.write('%s,%s,%s\n' %
                        (','.join(str(n) for n in a[0]), a[1][0], a[1][1]))
                self.handle.flush()
            else:
                # Avoid "dictionary changed size during iteration" exception
                new_attacks[target_turn] = attacks
        self.attacks = new_attacks

    def handle_player_turn(self):
        self.logger.debug("Handling player {} ({}) turn".format(self.current_player.get_name(), self.current_player.nickname))
        player = self.current_player.get_name()
        msg = self.get_message(player)

        if msg['type'] == 'battle':
            self.nb_consecutive_end_of_turns = 0
            # Record the attack
            self.attack(msg['atk'], msg['def'])
            battle = self.battle(self.board.get_area_by_name(msg['atk']), self.board.get_area_by_name(msg['def']))
            self.summary.add_battle()
            self.logger.debug("Battle result: {}".format(battle))
            for p in self.players:
                self.send_message(self.players[p], 'battle', battle=battle)
        elif msg['type'] == 'end_turn':
            # Flush old attacks
            self.nb_consecutive_end_of_turns += 1
            self.flush_attacks()
            self.turn_counter += 1
            affected_areas = self.end_turn()
            for p in self.players:
                self.send_message(self.players[p], 'end_turn', areas=affected_areas)
