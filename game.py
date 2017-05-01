from uuid import uuid4
from player_class import Player
from card_enterprise_class import EnterpriseCard
from card_sight_class import SightCard


class Game:

    def __init__(self):

        self.id = uuid4()
        self.status = 'WAIT'
        self.player_dict = dict()

    def add_player(self, player):

        self.player_dict[player.peer] = player

    def pop_player(self, player_peer):

        self.player_dict.pop(player_peer)

    def recv_message(self, player_peer, payload, is_binary):

        if is_binary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        self.player_dict[player_peer].sendMessage(payload, is_binary)

    def start(self):

        self.status = 'PLAYING'

    def stop(self):

        pass