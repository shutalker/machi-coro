#!/usr/bin/python3
# -*- coding: utf-8 -*-

from autobahn.twisted.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from twisted.internet import stdio
from mc_client_handler.client_IO_handler import GameClientIO


class GameClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):

        print('Соединение с сервером {0} установлено.'.format(response.peer))

    def onOpen(self):

        self.factory.connection_open(self)

    def onClose(self, wasClean, code, reason):

        self.factory.connection_close(self)

    def onMessage(self, payload, isBinary):

        self.factory.parse_message(self, payload, isBinary)


class GameClientFactory(WebSocketClientFactory):

    def __init__(self, *args, **kwargs):

        super(GameClientFactory, self).__init__(*args, **kwargs)

        self.connection_lose_flag = False
        self.clientIO = GameClientIO()

    def process_input(self, message):

        print(message)

    def connection_open(self, protocol):

        print('Соединение открыто.')
        print('Ожидание подключения остальных игроков...')
        print('-------------------------------------------------------------')
        print('\tДобро пожаловать в игру "Мачи-коро"!')
        print('\tСписок доступных команд:')
        print('\t\t"help [command]" - справка по доступным командам')
        print('\t\t"rules" - правила игры')
        print('\t\t"card [name]" - список всех карт/информация о карте')
        print('\t\t"hand" - список карт на руках')
        print('\t\t"bank" - текущий размер Вашего банка')
        print('\t\t"quit" - выход из игры')
        print('-------------------------------------------------------------')

        self.clientIO.game_protocol = protocol
        stdio.StandardIO(self.clientIO)

    def connection_close(self, protocol):

        print('Отключение от игры...')
        self.connection_lose_flag = True
        if reactor.running:
            reactor.stop()

    def parse_message(self, protocol, payload, is_binary):

        '''
            Парсинг сообщений от сервера
        '''

        message = payload.decode('utf-8')
        parsed_message = message.split(sep=':', maxsplit=1)
        message_type = parsed_message[0]

        # сообщения широковещатльной рассылки игрокам
        if message_type == 'bcast' or message_type == 'info':
            self.clientIO.print_message(parsed_message[1])
            if self.clientIO.request_desc:
                self.clientIO.print_message(self.clientIO.request_desc)

            return

        if message_type == 'pass_turn_request':
            self.clientIO.reset_request_processing_mode()
            self.clientIO.print_message('Вы пропускаете ход!')

            return

        if message_type == 'close_connection_request':
            self.clientIO.stopProducing()
            protocol.sendClose()

            return

        self.clientIO.process_server_request(*parsed_message)


if __name__ == '__main__':

    from twisted.internet import reactor
    from optparse import OptionParser
    import sys

    usage = "Usage: " + sys.argv[0] + " -a #server_address -p #server_port"
    parser = OptionParser(usage)
    parser.add_option("-a", "--address", dest="server_address",
                      help="server ipv4 address")
    parser.add_option("-p", "--port", dest="server_port",
                      help="port of server app")

    (options, args) = parser.parse_args()

    addr = options.server_address

    if options.server_port:
        try:
            port = int(options.server_port)
        except ValueError:
            print("Incorrect value of server port: " + options.server_port)
            sys.exit()
    else:
        port = 9000

    url = "ws://127.0.0.1:" + str(port)

    factory = GameClientFactory(url)
    factory.protocol = GameClientProtocol

    reactor.connectTCP(addr, port, factory)
    reactor.run()