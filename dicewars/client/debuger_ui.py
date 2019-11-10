import logging
import itertools

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel
from PyQt5.QtGui import QPainter, QColor, QPolygon, QPen, QBrush, QFont
from PyQt5.QtCore import QPoint, Qt, QRectF, QTimer

from .ui import Battle, MainWindow, Score, StatusArea


area_descriptors = [
    ('dice', lambda area: str(area.get_dice())),
    ('name', lambda area: str(area.get_name())),
]


def descriptors_provider():
    for i in itertools.count(0):
        yield area_descriptors[i % len(area_descriptors)]


class DebuggerUI(QWidget):
    """Dice Wars' graphical user interface
    """
    def __init__(self, game):
        """
        Parameters
        ----------
        game : Game
        """
        super().__init__()
        self.logger = logging.getLogger('GUI')
        self.game = game
        self.window_name = 'Debugger - Player ' + str(self.game.player_name)
        self.init_ui()

        self.area_text_fn_it = descriptors_provider()
        self.handle_change_labels_button()

        self.socket_timer = QTimer()
        self.socket_timer.timeout.connect(self.check_socket)
        self.socket_timer.start(10)
        self.game.battle = False
        self.game.draw_battle = False

    def init_ui(self):
        self.resize(1024, 576)
        self.setMinimumSize(1024, 576)
        self.setWindowTitle(self.window_name)

        self.init_layout()
        self.show()

    def init_layout(self):
        grid = QGridLayout()

        self.main_area = MainWindow(self.game, lambda area: str(area.get_name()))
        self.battle_area = Battle(self.game)
        self.score_area = Score(self.game)
        self.status_area = StatusArea(self.game)

        self.change_labels = QPushButton('Relabel')
        self.change_labels.clicked.connect(self.handle_change_labels_button)
        self.change_labels.setEnabled(True)

        grid.addWidget(self.main_area, 0, 0, 10, 8)
        grid.addWidget(self.battle_area, 0, 8, 4, 3)
        grid.addWidget(self.score_area, 4, 8, 4, 3)
        grid.addWidget(self.change_labels, 8, 9, 1, 1)
        grid.addWidget(self.status_area, 9, 8, 1, 3)

        self.setLayout(grid)

    def handle_change_labels_button(self):
        name, fn = next(self.area_text_fn_it)
        print('relabeling to {}'.format(name))
        self.main_area.set_area_text_fn(fn)
        self.main_area.update()
        self.change_labels.setText(name)

    def check_socket(self):
        """Check server message queue for incoming messages
        """
        if not self.game.input_queue.empty():
            event = self.game.input_queue.get()
            if not self.handle_server_message(event):
                self.logger.debug('Game has ended.')

    def handle_server_message(self, event):
        """Handle event associated to message from server
        """
        self.game.draw_battle = False

        try:
            msg = event
        except JSONDecodeError as e:
            self.logger.debug(e)
            self.logger.debug('msg = {}'.format(event))
            exit(1)

        if msg['type'] == 'battle':
            self.game.draw_battle = True
            atk_data = msg['result']['atk']
            def_data = msg['result']['def']
            self.logger.debug(type(atk_data['name']))
            attacker = self.game.board.get_area(str(atk_data['name']))
            attacker.set_dice(atk_data['dice'])
            atk_name = attacker.get_owner_name()

            defender = self.game.board.get_area(def_data['name'])
            defender.set_dice(def_data['dice'])
            def_name = defender.get_owner_name()

            if def_data['owner'] == atk_data['owner']:
                defender.set_owner(atk_data['owner'])
                self.game.players[atk_name].set_score(msg['score'][str(atk_name)])
                self.game.players[def_name].set_score(msg['score'][str(def_name)])

            self.game.battle = {
                'atk_name': atk_name,
                'def_name': def_name,
                'atk_dice': atk_data['pwr'],
                'def_dice': def_data['pwr']
            }

        elif msg['type'] == 'end_turn':
            self.logger.debug(msg)
            areas_to_redraw = []
            for area in msg['areas']:
                areas_to_redraw.append(self.game.board.get_area(int(area)))

            for a in areas_to_redraw:
                self.logger.debug(a)
            for area in msg['areas']:
                owner_name = msg['areas'][area]['owner']

                area_object = self.game.board.get_area(int(area))

                area_object.set_owner(owner_name)
                area_object.set_dice(msg['areas'][area]['dice'])

            self.game.players[self.game.current_player_name].deactivate()
            self.game.current_player_name = msg['current_player']
            self.game.current_player = self.game.players[msg['current_player']]
            self.game.battle = False
            self.game.players[self.game.current_player_name].activate()

            for i, player in self.game.players.items():
                player.set_reserve(msg['reserves'][str(i)])

        elif msg['type'] == 'game_end':
            if msg['winner'] == self.game.player_name:
                print("YOU WIN!")
            else:
                print("Player {} has won".format(msg['winner']))
            self.game.socket.close()
            exit(0)

        self.main_area.update()
        self.battle_area.update()
        self.score_area.update()
        self.status_area.update()

        if self.game.player_name == self.game.current_player.get_name():
            self.end_turn.setEnabled(True)
        else:
            self.end_turn.setEnabled(False)

        return True
