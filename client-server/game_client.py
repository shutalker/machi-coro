from autobahn.twisted.websocket import WebSocketClientProtocol


class MyClientProtocol(WebSocketClientProtocol):

    def clientInput(self):
        msg = str(input(">>> "))

        if msg == 'quit':
            self.sendClose()

        # self.sendMessage(msg.encode('utf-8'))

    def onConnect(self, response):
        print('Connected to server {0}'.format(response.peer))

    def onOpen(self):
        print('Connection successfully opened')
        #self.clientInput()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        reactor.stop()

    def onMessage(self, payload, isBinary):

        message = payload.decode('utf-8')
        print("Message received: {0}".format(message))

        if message == 'close_connection_request':
            self.sendClose()
        else:
            self.clientInput()


if __name__ == '__main__':
    
    from twisted.internet import reactor

    from autobahn.twisted.websocket import WebSocketClientFactory
    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyClientProtocol

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()