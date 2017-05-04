from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from game_logic.game import Game
from threading import Thread
import MySQLdb


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

        # колода карт резерва и атрибуты всех карт. Вытягиваются из базы данных
        # единажды при запуске сервера
        self.card_heap = dict()
        self.cards_properties = dict()

        # под каждую игру создается отдельный поток (да, плохо, я знаю, но
        # решения лучше не придумал, как написать корутину для game.start() -
        # не знаю)
        self.game_threads = dict()

        self.get_cards_from_db()

    def get_cards_from_db(self):

        try:
            db = MySQLdb.connect(host="localhost", db="machi_coro",
                                 read_default_file="./.my.cnf")

            # курсор для данных о картах предприятий
            cursor_enterprise = db.cursor()
            e_row_amount = cursor_enterprise.execute('''SELECT name, price, 
                                                     effect_cost, description, 
                                                     profit_type, branch_type, 
                                                     profit_margin, amount
                                                     FROM card c JOIN enterprise e
                                                     ON c.id = e.card_id''')
            # курсор для данных о достопримечательностях
            cursor_sight = db.cursor()
            s_row_amount = cursor_sight.execute('''SELECT name, price, 
                                                effect_cost, description, 
                                                effect_name
                                                FROM card c JOIN sight s
                                                ON c.id = s.card_id''')

        except MySQLdb.Error:
            raise
            reactor.stop()

        if e_row_amount < 1 or s_row_amount < 1:
            print("Empty database!")
            reactor.stop()

        for _ in range(e_row_amount):
            props = cursor_enterprise.fetchone()
            self.cards_properties[props[0]] = {
                'name' : props[0],
                'price' : props[1],
                'effect_cost' : props[2],
                'description' : props[3],
                'profit_type' : props[4],
                'branch_type' : props[5],
                'profit_margin' : props[6]
            }
            self.card_heap[props[0]] = props[7]

        for _ in range(s_row_amount):
            props = cursor_sight.fetchone()
            self.cards_properties[props[0]] = {
                'name' : props[0],
                'price' : props[1],
                'effect_cost' : props[2],
                'description' : props[3],
                'effect_name' : props[4]
            }

        cursor_enterprise.close()
        cursor_sight.close()

    def add_to_game(self, player):

        if self.current_lobby_size == 0:
            new_game = Game(self.card_heap, self.cards_properties)
            self.last_created_game_id = new_game.id
            self.games[self.last_created_game_id] = new_game

        self.games[self.last_created_game_id].add_player(player)
        self.current_lobby_size += 1

        if self.current_lobby_size >= 2:
            game = self.games[self.last_created_game_id]
            self.game_threads[game.id] = Thread(target=game.start)
            self.game_threads[game.id].start()
            self.current_lobby_size = 0

    def pop_from_game(self, player):

        for game_id in self.games:
            game = self.games[game_id]

            if player.peer in game.peers:
                game.pop_player(player.peer)

                if game.status == 'WAIT':
                    self.current_lobby_size -= 1

                if len(game.players) < 1:
                    # last_peer = game.peers.popitem()
                    # last_peer[1]['transport'].connectionLost('reason')
                    game.stop()
                    self.game_threads[game.id].join()
                    print("Game " + str(game.id) + " has been finished")
                    self.game_threads.pop(game.id)
                    self.games.pop(game.id)

                break

    def process_message(self, player, payload, isBinary):

        for game_id in self.games:
            game = self.games[game_id]
            print('Trying game ' + str(game_id))
            if player.peer in game.peers:
                print('Message for ' + str(game.id))
                game.recv_msg(player.peer, payload, isBinary)
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