from autobahn.twisted.websocket import WebSocketClientProtocol


class MyClientProtocol(WebSocketClientProtocol):

    def clientInput(self):
        msg = str(input(">>> "))

        if(len(msg) == 0):
            self.sendClose(code=1000, reason='GoodBye!')

        self.sendMessage(msg.encode('utf-8'))

    def onConnect(self, response):
        print('Connected to server {0}'.format(response.peer))

    def onOpen(self):
        print('Connection successfully opened')
        self.clientInput()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        reactor.stop()

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        self.clientInput()


if __name__ == '__main__':
    
    from twisted.internet import reactor

    from autobahn.twisted.websocket import WebSocketClientFactory
    factory = WebSocketClientFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyClientProtocol

    reactor.connectTCP("127.0.0.1", 9000, factory)
    reactor.run()