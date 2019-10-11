import re


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
        repr_re = re.compile(r''' Winner:\ (?P<winner>.+)\n Battles\ total:\ (?P<nb_battles>.+)\n ''', re.VERBOSE | re.MULTILINE)

        m = repr_re.match(str_repr)
        winner = m.group('winner')
        nb_battles = int(m.group('nb_battles'))

        summary = cls()
        summary.set_winner(winner)
        summary.nb_battles = nb_battles
        return summary


def get_win_rates(summaries, nb_players):
    nb_wins = {str(i): 0 for i in range(1, nb_players+1)}

    for summary in summaries:
        nb_wins[summary.winner] += 1

    return nb_wins
