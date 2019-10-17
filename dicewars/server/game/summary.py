from collections import defaultdict


class GameSummary(object):
    def __init__(self):
        self.winner = None
        self.nb_battles = 0

    def set_winner(self, winner):
        assert(self.winner is None)
        self.winner = winner

    def add_battle(self):
        self.nb_battles += 1

    def __repr__(self):
        winner_str = 'Winner: {}\n'.format(self.winner)
        nb_battles_str = 'Battles total: {}\n'.format(self.nb_battles)
        total_str = winner_str + nb_battles_str
        return total_str

    @classmethod
    def from_repr(cls, str_repr):
        lines = str_repr.split('\n')

        winner = lines[0].split(maxsplit=1)[1]
        nb_battles = int(lines[1].split()[2])

        summary = cls()
        summary.set_winner(winner)
        summary.nb_battles = nb_battles
        return summary


def get_win_rates(summaries, nb_players):
    nb_wins = defaultdict(int)

    for summary in summaries:
        nb_wins[summary.winner] += 1

    return dict(nb_wins)
