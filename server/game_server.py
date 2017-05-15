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

        # запросы от клиентов, которые не влияют на игровую логику и
        # обрабатываются сразу
        self.outter_requests = [
            'card_info_request',
            'all_cards_request',
            'player_bank_request',
            'player_hand_request'
        ]

        self.get_cards_from_db()

    def get_cards_from_db(self):

        '''
            Вытягивание информации об игровых картах. Выполняется единажды
            при старте сервера, поэтому блокировками при вызовах execute
            можно пренебресь (на первых версиях реализации)
        '''

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
            new_game = Game(self.card_heap, self.cards_properties, 100)
            self.last_created_game_id = new_game.id
            self.games[self.last_created_game_id] = new_game
            print('Game ' + str(new_game.id) + ' created')

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

            if player.peer in game.request_handler.peers:
                game.pop_player(player.peer)

                # если игра еще не началась, то просто уменьшется размер
                # текущего лобби игроков
                if game.status == 'WAIT':
                    self.current_lobby_size -= 1
                    if self.current_lobby_size < 1:
                        self.games.pop(game.id)
                        print('Game ' + str(game.id) + ' has been destroyed')

                    break

                # если в игре остался только 1 игрок, то игра завершается
                if game.status == 'PLAYING':
                    if len(game.players) < 2:
                        last_player_id = game.players.popitem()[0]
                        request = 'close_connection_request'
                        game.stop()
                        game.request_handler.send_request(last_player_id,
                                                          request)
                        self.game_threads[game.id].join()
                        self.game_threads.pop(game.id)

                        print('Game ' + str(game.id) + ' has been finished')
                        self.games.pop(game.id)

                    break

    def process_message(self, player, payload, isBinary):

        '''
            Обработка входящих запросов (ответов)
        '''

        request = payload.decode('utf-8').split(sep=':')

        # обработка запросов, не относящихся к игровой логике
        if request[0] in self.outter_requests:
            command =  'outter_' + request[0]
            request_handler = getattr(self, command)
            request_handler(player, *request)

            return

        for game_id in self.games:
            game = self.games[game_id]
            print('Trying game ' + str(game_id))
            if player.peer in game.request_handler.peers:
                print('Message for ' + str(game.id))
                game.request_handler.recv_msg(player.peer, payload, isBinary)
                break

    def outter_card_info_request(self, player_protocol, *args):

        '''
            Отсылка клиенту информации об указанной им карте
        '''

        card_name = args[1]
        response = 'info:'

        if card_name in self.cards_properties:
            card = self.cards_properties[card_name]
            response += 'Карта: ' + card['name'] + '\r\n'
            response += 'Cтоимость: ' + str(card['price']) + '\r\n'
            response += 'Описание: ' + card['description'] + '\r\n'
            response += 'Стоимость эффекта (диапазон): ' + \
                        card['effect_cost']
        else:
            response += 'Имя карты указано неверно!'

        player_protocol.sendMessage(response.encode('utf-8'), True)

    def outter_all_cards_request(self, player_protocol, *args):

        '''
            Остылка клиенту названий всех карт игры
        '''

        response = 'info:'

        for card_name in self.cards_properties:
            response += card_name + '\r\n'

        player_protocol.sendMessage(response.encode('utf-8'), True)

    def outter_player_bank_request(self, player_protocol, *args):

        '''
            Отсылка текущего банка запрашивающему игроку
        '''

        response = 'info:'

        for game_id in self.games:
            game = self.games[game_id]

            if player_protocol.peer in game.request_handler.peers:
                peer = game.request_handler.peers[player_protocol.peer]
                player_id = peer['player_id']
                player_bank = game.players[player_id].bank

                response += 'Ваш текущий банк: ' + str(player_bank)
                response += ' монет(а/ы)'
                player_protocol.sendMessage(response.encode('utf-8'), True)

    def outter_player_hand_request(self, player_protocol, *args):

        '''
            Отсылка карт, имеющихся на руках у игрока
        '''

        response = 'info:'

        for game_id in self.games:
            game = self.games[game_id]

            if player_protocol.peer in game.request_handler.peers:
                peer = game.request_handler.peers[player_protocol.peer]
                player_id = peer['player_id']
                player = game.players[player_id]

                response += 'Предприятия:' + '\r\n'
                for card_name in player.enterprise_card_hand:
                    card = player.enterprise_card_hand[card_name]
                    card_amount = card.hand_card_amount
                    response += card_name + ' x ' + str(card_amount) + '\r\n'

                response += '\r\n' + 'Достопримечательности:' + '\r\n'
                for card_name in player.sight_card_hand:
                    response += card_name + '\r\n'

                player_protocol.sendMessage(response.encode('utf-8'), True)

if __name__ == '__main__':

    import sys
    from twisted.internet import reactor
    from twisted.python import log

    log.startLogging(sys.stdout)

    factory = GameServerFactory(u"ws://0.0.0.0:9000")
    factory.protocol = GameServerProtocol

    reactor.listenTCP(9000, factory)
    reactor.run()