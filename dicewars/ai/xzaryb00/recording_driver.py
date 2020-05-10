from dicewars.client.ai_driver import AIDriver

class RecordingAIDriver(AIDriver):

    def __init__(self, game, ai_constructor):
        super().__init__(game, ai_constructor)
        self.attacks = {}
        self.handle = open('turns.csv', 'a')

    def attack(self, atk_name, def_name):
        features = get_features(self.game.board, atk_name, def_name)
        atk_owner = features[2][0]
        self.attacks.setdefault((self.turns_finished, atk_owner), []).append(features)

    def age(self, new_player):
        new_attacks = {}
        for (turn_no, player), attacks in self.attacks.items():
            if player != new_player and not self.game.players[player].activated:
                new_attacks[(turn_no, player)] = attacks
                continue
            for a in attacks:
                # If the attacker held the atk/def areas in prev turns but holds
                # them no longer, then flip output values to zero
                if a[1][0] and a[2][0] != a[2][1].owner_name:
                    a[1][0] = 0
                if a[1][1] and a[2][0] != a[2][2].owner_name:
                    a[1][1] = 0
            if (turn_no + self.area_kept_turns) <= self.turns_finished:
                # Flush too-old attacks
                for a in attacks:
                    self.handle.write('%s,%s,%s\n' %
                        (','.join(str(n) for n in a[0]), a[1][0], a[1][1]))
                self.handle.flush()
            else:
                # Avoid "dictionary changed size during iteration" exception
                new_attacks[(turn_no, player)] = attacks
        self.attacks = new_attacks

    def handle_server_message(self, msg):
        try:
            if msg['type'] == 'battle':
                self.attack(msg['result']['atk']['name'], msg['result']['def']['name'])
            elif msg['type'] == 'end_turn':
                # Age attacks at the start of our turn
                self.age(msg['current_player'])
            elif msg['type'] == 'game_end':
                # Flush remaining attacks
                self.age(-1)
                self.handle.close()
        except Exception as e:
            print(e)
            raise e
        return super().handle_server_message(msg)
