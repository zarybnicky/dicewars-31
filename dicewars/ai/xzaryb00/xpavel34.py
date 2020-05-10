"""
Autor: Ondřej Pavela - xpavel34
----------

Implementace Q-Learning metody posilovaného učení
Pro aproximaci funkce Q* je použita neuronová síť,
která na vstupu dostane vektor příznaků vhodně popisující
herní pole a na výstupu hodnoty Q funkce.

Příznaky jsou reprezentovány maticí o rozměru 31 * 30
(maximální velikost pole je 31, každé pole může mít teoreticky
 až 30 sousedních polí)
Kladná hodnota na indexu [x][y] reprezentuje šanci na výhru
při napadení x -> y. Pro všechny okolní pole 'y' je spočtena
šance výhry při odvetném napadení za předpokladu, že útok x -> y
byl úspěšný.

Zbytek tvoří standardní implementace algoritmu pro Q-learning.
Systém odměn je velmi triviální, viz kód. Bohužel jsme nestihli
výslednou síť natrénovat a vyladit systém odměn a také hyperparametry
sítě. Při trénování nové sítě bylo toto AI schopno vyhrát 5/10 prvních
trénovacích her proti AI 'STEi' a prvních 13/50 proti AI 'pwm_c'.

"""


import math
import random
import logging
import torch
import torch.autograd
import torch.nn as nn
import torch.optim as optim
import sys
import pickle
import pathlib
from collections import deque

import dicewars.ai.utils as utils
import scripts.utils as script_utils
from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


MAX_BOARD_SIZE = 31
MODEL_PATH = './dqn.model'
REPLAY_MEMORY_PATH = './replay_memory.data'


class ReplayBuffer:
    def __init__(self, buffer_size):
        self.buffer_size = buffer_size
        self.count = 0
        self.buffer = deque()

    def add(self, s, a, s2, r, d, s_indices, s2_indices):
        experience = [s, a, s2, r, d, s_indices, s2_indices]
        if self.count < self.buffer_size:
            self.buffer.append(experience)
            self.count += 1
        else:
            self.buffer.popleft()
            self.buffer.append(experience)

    def size(self):
        return self.count

    def sample(self, batch_size):
        batch = random.sample(self.buffer, min(self.count, batch_size))

        state_batch = torch.cat(tuple(d[0] for d in batch))
        action_batch = torch.cat(tuple(d[1] for d in batch))
        next_state_batch = torch.cat(tuple(d[2] for d in batch))
        reward_batch = torch.cat(tuple(d[3] for d in batch))
        terminal_batch = torch.cat(tuple(d[4] for d in batch))
        s_indices_batch = [d[5] for d in batch]
        s2_indices_batch = [d[6] for d in batch]

        return state_batch, action_batch, next_state_batch, reward_batch, \
               terminal_batch, s_indices_batch, s2_indices_batch

    def clear(self):
        self.buffer.clear()
        self.count = 0


class DQN(nn.Module):
    def __init__(self):
        super(DQN, self).__init__()
        self.steps_done = 0
        self.enable_training = True

        # Maximum of 31 areas, each can have up to 30 neighbours: 31 * 30
        self.number_of_actions = MAX_BOARD_SIZE * (MAX_BOARD_SIZE - 1)

        self.gamma = 0.99
        self.minibatch_size = 32

        self.eps_start = 0.9
        self.eps_end = 0.05
        self.eps_decay = 200

        self.fc1 = nn.Linear(self.number_of_actions, 256)
        self.relu1 = nn.ReLU(inplace=True)
        self.fc2 = nn.Linear(256, 128)
        self.relu2 = nn.ReLU(inplace=True)
        self.fc3 = nn.Linear(128, self.number_of_actions)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        return x

    def select_action(self, state, valid_action_indices):
        action_count = len(valid_action_indices)

        with torch.no_grad():
            if self.enable_training:
                sample = random.random()
                if sample < 0.15:
                    # Skip turn
                    return torch.zeros([self.number_of_actions], dtype=torch.float32), None

                eps_threshold = self.eps_end + (self.eps_start - self.eps_end) * math.exp(
                    -1. * self.steps_done / self.eps_decay)
                self.steps_done += 1

                if sample > eps_threshold:
                    output = self(state)
                    valid_outputs = torch.empty(action_count, dtype=torch.float32)
                    for i, action_index in enumerate(valid_action_indices):
                        valid_outputs[i] = output[action_index].item()
                    q_values = valid_outputs.softmax(0)
                    q_value, q_value_index = q_values.max(0)
                    output.zero_()
                    output[valid_action_indices[q_value_index]] = 1
                    return output, q_value_index  # Return action vector and action index
                else:
                    action_index = torch.randint(action_count, torch.Size([]), dtype=torch.int)
                    action_vector = torch.zeros([self.number_of_actions], dtype=torch.float32)
                    action_vector[valid_action_indices[action_index]] = 1
                    return action_vector, action_index

            else:
                output = self(state)
                valid_outputs = torch.empty(action_count, dtype=torch.float32)
                for i, action_index in enumerate(valid_action_indices):
                    valid_outputs[i] = output[action_index].item()
                return None, valid_outputs.softmax(0).argmax(0)

    def save_network(self, path):
        torch.save(self.state_dict(), path)

    def load_network(self, path):
        self.load_state_dict(torch.load(path))


def filter_dqn_output(dqn_batch_output, indices_batch):
    valid_output_batch = []
    for idx in range(len(dqn_batch_output)):
        valid_action_indices = indices_batch[idx]
        dqn_output = dqn_batch_output[idx]
        action_count = len(valid_action_indices)
        if action_count > 0:
            valid_outputs = torch.empty(action_count, dtype=torch.float32)
            for i, action_index in enumerate(valid_action_indices):
                valid_outputs[i] = dqn_output[action_index].item()
            valid_outputs = valid_outputs.softmax(0)
        else:
            valid_outputs = torch.empty(1, dtype=torch.float32)
            valid_outputs[0] = 0
        dqn_output.zero_()
        for i, action_index in enumerate(valid_action_indices):
            dqn_output[action_index] = valid_outputs[i].item()

        valid_output_batch.append(valid_outputs)

    return valid_output_batch, dqn_batch_output


def possible_counterattacks(board, contested_area, next_owner):
    neighbours = contested_area.get_adjacent_areas()
    valid_attacks = []
    for adj in neighbours:
        adjacent_area = board.get_area(adj)
        if adjacent_area.can_attack() and adjacent_area.get_owner_name() != next_owner:
            valid_attacks.append((adjacent_area, contested_area))

    return valid_attacks


def extract_features(board, possible_attacks):
    feature_vector = torch.zeros([MAX_BOARD_SIZE, MAX_BOARD_SIZE - 1], dtype=torch.float32)
    action_indices = []
    for (source, target) in possible_attacks:
        probability = utils.probability_of_successful_attack(board, source.name, target.name)
        x = source.name - 1
        y = target.name - 1 if target.name < source.name else target.name - 2
        action_indices.append(x * (MAX_BOARD_SIZE - 1) + y)
        feature_vector[x][y] = probability

        counterattacks = possible_counterattacks(board, target, source.get_owner_name())
        new_defense_power = source.get_dice() - 1
        for (counter_source, contested_area) in counterattacks:
            attack_power = counter_source.get_dice()
            counterattack_probability = utils.attack_succcess_probability(attack_power, new_defense_power)
            x = counter_source.name - 1
            y = contested_area.name - 1 if contested_area.name < counter_source.name else contested_area.name - 2
            feature_vector[x][y] = -counterattack_probability

    feature_vector = feature_vector.flatten()
    return feature_vector, action_indices


class AI:
    def __del__(self):
        if self.dqn.enable_training:
            self.dqn.save_network(MODEL_PATH)
            try:
                with open(REPLAY_MEMORY_PATH, 'wb') as f:
                    pickle.dump(self.replay_memory.buffer, f)
            except Exception as e:
                print(e)

    def __init__(self, player_name, board, players_order):
        try:
            self.dqn = DQN()
            self.dqn_optimizer = optim.Adam(self.dqn.parameters(), lr=1e-6)
            self.dqn_criterion = nn.MSELoss()

            self.replay_memory_size = 10000
            self.replay_memory = ReplayBuffer(self.replay_memory_size)

            self.player_name = player_name
            self.logger = logging.getLogger('AI')

            #  For reward calculations
            self.region_count = len(board.get_players_regions(self.player_name))
            self.area_count = len(board.get_player_areas(self.player_name))
            self.dice_count = board.get_player_dice(self.player_name)
            self.move_count = 0

            self.reward_eps_start = 1.0
            self.reward_eps_end = 0.01
            self.reward_eps_decay = 5

            if self.dqn.enable_training and pathlib.Path(REPLAY_MEMORY_PATH).exists():
                with open(REPLAY_MEMORY_PATH, 'rb') as f:
                    self.replay_memory.buffer = pickle.load(f)
                    self.replay_memory.count = len(self.replay_memory.buffer)

            file = pathlib.Path(MODEL_PATH)
            if file.exists():
                self.dqn.load_network(MODEL_PATH)
            else:
                print("[AI] Missing model file: " + str(MODEL_PATH))
                self.dqn.save_network(MODEL_PATH)

        except Exception as e:
            print(e)

    # Calculate reward decay rate based on how much in the past was
    # the action taken relative to the latest end turn
    def calculate_reward_decay(self, t_minus):
        return self.reward_eps_end + \
               (self.reward_eps_start - self.reward_eps_end) * math.exp(-1.0 * (t_minus / self.reward_eps_decay))

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        try:
            self.logger.debug("[AI] Starting turn")
            attacks = list(utils.possible_attacks(board, self.player_name))
            current_state, action_indices = extract_features(board, attacks)

            if self.replay_memory.count > 0:
                # Set remaining values after evaluation of next state by the game engine
                last_memory = self.replay_memory.buffer[-1]
                last_memory[2] = current_state
                last_memory[3] = torch.tensor([0], dtype=torch.float32)
                last_memory[6] = action_indices

                if nb_moves_this_turn > 0:
                    # Mid turn adjustments
                    reward = board.get_player_dice(self.player_name) - self.dice_count
                    reward = reward + 10 if reward == 0 else reward
                    last_memory = self.replay_memory.buffer[-1]
                    last_memory[3] += reward
                else:
                    previous_area_count = self.area_count
                    previous_region_count = self.region_count
                    self.region_count = len(board.get_players_regions(self.player_name))
                    self.area_count = len(board.get_player_areas(self.player_name))
                    area_count_delta = self.area_count - previous_area_count
                    region_count_delta = self.region_count - previous_region_count

                    # Adjust rewards of actions taken in previous
                    # turn based on board power difference
                    reward = (area_count_delta * 50) - (region_count_delta * 100)
                    if area_count_delta == 0:
                        reward += 25
                    if region_count_delta == 0:
                        reward += 50
                    for i in range(1, self.move_count + 1):
                        decay_rate = self.calculate_reward_decay(i - 1)
                        past_memory = self.replay_memory.buffer[-i]
                        past_memory[3] += reward * decay_rate

                    if self.replay_memory.count >= self.dqn.minibatch_size:
                        # Sample replay memory
                        state_batch, action_batch, next_state_batch, \
                        reward_batch, terminal_batch, \
                        s_indices_batch, s2_indices_batch = self.replay_memory.sample(self.dqn.minibatch_size)

                        # Reshape to (32,930)
                        state_batch = state_batch.reshape((self.dqn.minibatch_size, self.dqn.number_of_actions))
                        action_batch = action_batch.reshape((self.dqn.minibatch_size, self.dqn.number_of_actions))
                        next_state_batch = next_state_batch.reshape(
                            (self.dqn.minibatch_size, self.dqn.number_of_actions))

                        next_valid_batch, next_filtered_batch = \
                            filter_dqn_output(self.dqn(next_state_batch), s2_indices_batch)

                        y_batch = torch.cat(tuple(torch.tensor([1000], dtype=torch.float32) if terminal_batch[i]
                                                  else reward_batch[i].unsqueeze(0) + self.dqn.gamma * torch.max(
                            next_valid_batch[i])
                                                  for i in range(len(next_valid_batch))))

                        state_filtered_batch = filter_dqn_output(self.dqn(state_batch), s_indices_batch)[1]
                        for i in range(0, self.dqn.minibatch_size):
                            state_filtered_batch[i] *= action_batch[i]

                        q_value = torch.sum(state_filtered_batch, dim=1)
                        self.dqn_optimizer.zero_grad()

                        y_batch = y_batch.detach()
                        loss = self.dqn_criterion(q_value, y_batch)
                        loss.backward()
                        self.dqn_optimizer.step()

            if not attacks:
                self.logger.debug("[AI] No more possible turns")
                self.move_count = nb_moves_this_turn + 1
                return EndTurnCommand()

            action_vector, action_index = self.dqn.select_action(current_state, action_indices)

            self.dice_count = board.get_player_dice(self.player_name)
            self.replay_memory.add(current_state, action_vector, None,
                                   torch.tensor([0], dtype=torch.float32),
                                   torch.tensor([False], dtype=torch.bool), action_indices, None)

            if action_index is None:
                self.logger.debug("[AI] Ending turn")
                self.move_count = nb_moves_this_turn + 1
                return EndTurnCommand()

            source, target = attacks[action_index.item()]
            return BattleCommand(source.get_name(), target.get_name())

        except Exception as e:
            print(e)


UNIVERSAL_SEED = 42
PLAYING_AIs = [
    'xpavel34',
    # 'dt.rand',
    # 'dt.sdc',
    # 'dt.ste',
    # 'dt.stei',
    # 'dt.wpm_d',
    # 'dt.wpm_s',
    'dt.wpm_c'
]

procs = []


def board_definitions(initial_board_seed):
    board_seed = initial_board_seed
    while True:
        yield script_utils.BoardDefinition(board_seed, UNIVERSAL_SEED, UNIVERSAL_SEED)
        board_seed += 1


def train_dqn(game_count):
    games_played = 0
    board_seed = 420
    game_size = 2
    combatants_provider = script_utils.EvaluationCombatantsProvider(PLAYING_AIs, 'xpavel34')
    reporter = script_utils.SingleLineReporter(False)

    try:
        combatants = combatants_provider.get_combatants(game_size)

        for board_definition in board_definitions(board_seed):
            if games_played == game_count:
                break

            games_played += 1

            reporter.report(f'{games_played}/{game_count} vs. {combatants}')
            game_summary = script_utils.run_ai_only_game(
                30021, '127.0.0.1', procs, combatants,
                board_definition,
                fixed=UNIVERSAL_SEED,
                client_seed=UNIVERSAL_SEED,
                logdir="./",
                debug=True,
            )
            print(f' Winner: {game_summary.winner}')
            if game_summary.winner == 'xpavel34 (AI)':
                replay_buffer = None
                with open(REPLAY_MEMORY_PATH, 'rb') as f:
                    replay_buffer = pickle.load(f)
                    replay_buffer[-1][4] = torch.tensor([True], dtype=torch.bool)
                if replay_buffer:
                    with open(REPLAY_MEMORY_PATH, 'wb') as f:
                        pickle.dump(replay_buffer, f)

    except (Exception, KeyboardInterrupt) as e:
        sys.stderr.write("Breaking the tournament because of {}\n".format(repr(e)))
        for p in procs:
            p.kill()


if __name__ == '__main__':
    train_dqn(50)
