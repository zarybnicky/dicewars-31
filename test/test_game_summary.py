import unittest

from server.game.summary import GameSummary


class GameSummaryTests(unittest.TestCase):
    def test_repr_loading(self):
        summary = GameSummary()
        summary.set_winner('joe')
        reconstructed = GameSummary.from_repr(repr(summary))
        self.assertEqual(repr(reconstructed), repr(summary))
