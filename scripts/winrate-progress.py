#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import pickle


class PlayerRecord:
    def __init__(self):
        self.nb_games = 0
        self.nb_wins = 0
        self.entries = []
        self.game_stamps = []

    def score_game(self, game_no, win):
        if len(self.game_stamps) > 0:
            assert(game_no > self.game_stamps[-1])
        self.game_stamps.append(game_no)

        self.nb_games += 1
        if win:
            self.nb_wins += 1

        self.entries.append((self.nb_games, self.nb_wins))

    @property
    def winrates(self):
        return [100.0*wins/games for games, wins in self.entries]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('games', help='where the games are stored')
    args = parser.parse_args()

    with open(args.games, 'rb') as f:
        games = pickle.load(f)

    players = {}
    nb_games_processed = 0
    for game in games:
        nb_games_processed += 1
        if game.winner not in players:
            players[game.winner] = PlayerRecord()
        players[game.winner].score_game(nb_games_processed, True)

        eliminated = [e[0] for e in game.eliminations]
        for loser in eliminated:
            if loser not in players:
                players[loser] = PlayerRecord()
            players[loser].score_game(nb_games_processed, False)

    plt.figure()
    for name, record in players.items():
        plt.plot(record.game_stamps, record.winrates, label=name)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
