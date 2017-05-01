from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from game import Game


class GameServerProtocol(WebSocketServerProtocol):

    def onOpen(self):
        self.factory.add_to_game(self)

    def onMessage(self, payload, isBinary):
        self.factory.process_message(self, payload, isBinary)

    def connectionLost(self, reason):
        self.factory.pop_from_game(self)


class GameServerFactory(WebSocketServerFactory):

    def __init__(self, *args, **kwargs):

        super(GameServerFactory, self).__init__(*args, **kwargs)

        # словарь игр. Каждая игра имеет уникальный id - ключ в словаре
        self.games = dict()

        # размер лобби, т.е. счетчик игроков, которые в данный момент находятся
        # в последнем созданном лобби. Если значение счетчика достигает
        # некоторого определенного, игра начинается, а для новых игроков
        # создается новое лобби
        self.current_lobby_size = 0

        # id последней игры, которая еще не началась (в ожидании игроков)
        self.last_created_game_id = None

    def add_to_game(self, player):

        if self.current_lobby_size == 0:
            new_game = Game()
            self.last_created_game_id = new_game.id
            self.games[self.last_created_game_id] = new_game

        self.games[self.last_created_game_id].add_player(player)
        self.current_lobby_size += 1

        if self.current_lobby_size >= 1:
            game = self.games[self.last_created_game_id]
            game.start()
            print("Game " + str(game.id) + " started")
            self.current_lobby_size = 0

    def pop_from_game(self, player):

        for game_id in self.games:
            game = self.games[game_id]

            if player.peer in game.player_dict:
                game.pop_player(player.peer)

                if game.status == 'WAIT':
                    self.current_lobby_size -= 1

                if len(game.player_dict) < 1:
                    print("Game " + str(game.id) + " has been finished")
                    game.stop()
                    self.games.pop(game.id)

                break

    def process_message(self, player, payload, isBinary):

        for game_id in self.games:
            game = self.games[game_id]
            print('Trying game ' + str(game_id))
            if player.peer in game.player_dict:
                print('Message for ' + str(game.id))
                game.recv_message(player.peer, payload, isBinary)
                break



if __name__ == '__main__':

    import sys
    from twisted.internet import reactor
    from twisted.python import log

    log.startLogging(sys.stdout)

    factory = GameServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = GameServerProtocol

    reactor.listenTCP(9000, factory)
    reactor.run()