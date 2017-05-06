class ServerRequestHandler:

    '''
        Обработчик запросов, исходящих от сервера клиентам в ходе игры
    '''

    def __init__(self):

        # ключ в словаре - player.peer (host id), значение - словарь:
        # ключи: transport, player_id
        self.peers = dict()

        # флаг ожидания сообщения
        self.message_recieved_flag = False

        # внутреигровой буфер сообщений
        self.message_buffer = ''

    def recv_msg(self, player_peer, payload, is_binary):

        '''
            Функция, вызывающаяся в ответ на callback onMessage на сервере.
            Осуществляет прием сообщения
        '''

        print("Message received: {0}".format(payload.decode('utf-8')))

        message = payload.decode('utf-8')
        self.message_buffer = message
        self.message_recieved_flag = True

    def send_request(self, player_id, request):
        
        '''
            Функция-дистпетчер обработки запросов от сервера клиентам
        '''

        parsed_request = request.split(sep=':', maxsplit=1)
        command = parsed_request[0]

        # выбор нужного метода обработки запроса
        request_handler = getattr(self, command)

        if len(parsed_request) > 1:
            request_arg = parsed_request[1]
        else:
            request_arg = None

        for peer in self.peers:
            if self.peers[peer]['player_id'] == player_id:
                player_protocol = self.peers[peer]['transport']

        return request_handler(player_protocol, command, request_arg)

    def broadcast(self, message):
        
        '''
            Рассылка сообщения всем игрокам
        '''

        payload = ('bcast:' + message).encode(encoding='utf-8')

        for player_peer in self.peers:
            self.peers[player_peer]['transport'].sendMessage(payload, True)

    def close_all_connections(self):

        for player_peer in self.peers:
            request = 'close_connection_request'
            self.send_request(self.peers[player_peer]['player_id'], request)

    def wait_for_message(self):

        while not self.message_recieved_flag:

            pass

        # когда сообщение пришло, флаг сбрасывается,
        # чтобы обрабатывать следующие сообщения
        self.message_recieved_flag = False

        response = self.message_buffer
        self.message_buffer = ''

        return response

    def player_name_request(self, player_protocol, request, request_arg):

        '''
            Функция запроса имени игрока
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)
        response = self.wait_for_message()

        if len(response) < 1:
            response = None

        return response

    def close_connection_request(self, player_protocol, request, request_arg):

        '''
            Функция разрыва связи с игроками
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)

    def dice_amount_request(self, player_protocol, request, request_arg):

        '''
            Функция запроса количества кубиков для выбрасывания
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)
        response = self.wait_for_message()

        return int(response)

    def reroll_dice_request(self, player_protocol, request, request_arg):

        '''
            Функция запроса перебрасывания кубика (одного из двух)
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)
        response = self.wait_for_message()

        dice_idx, result = None, None

        if response == 'reroll_accept':
            dice_amount = request_arg

            if dice_amount > 1:
                request = 'dice_idx_to_reroll_request'
                player_protocol.sendMessage(request.encode(encoding='utf-8'),
                                            True)
                response = self.wait_for_message()
                dice_idx = int(response)
            else:
                dice_idx = 0

            result = randint(1, 6)

        return dice_idx, result

    def increase_dice_score_request(self, player_protocol, request,
                                    request_arg):

        '''
            Функция запроса увеличения очков на кубиках
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)
        response = self.wait_for_message()

        increase_value = 0

        if response == 'increase_accept':
            increase_value = 2

        return increase_value

    def profit_request(self, player_protocol, request, request_arg):

        '''
            Функция отсылки дохода игрока на данном ходу
        '''

        profit_info = 'Ваш доход на этом ходу: '
        profit_info += request_arg
        profit_info += ' монет(а/ы)'

        request = request + ':' + profit_info
        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)

    def bank_loss_request(self, player_protocol, request, request_arg):

        '''
            Функция отсылки расхода игрока на данном ходу
        '''

        loss_info = 'Ваши убытки на этом ходу: '
        loss_info += request_arg
        loss_info += ' монет(а/ы)'

        request = request + ':' + loss_info
        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)

    def build_request(self, player_protocol, request, request_arg):

        '''
            Функция запроса строительства предприятий (строить или нет?)
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)
        response = self.wait_for_message()

        return response

    def profit_from_no_build_request(self, player_protocol, request,
                                     request_arg):

        '''
            Функция отправки сообщения о доходе при отказе от строительства
            (если построен "Аэропорт")
        '''

        player_protocol.sendMessage(request.encode(encoding='utf-8'), True)

    def build_choise_request(self, player_protocol, request, request_arg):

        '''
            Функция запроса строительства конкретного предприятия
        '''

        response = ''

        # если у игрока нет возможности построить ни одно предприятие
        # выбранного типа, то строка request_arg, формирующаяся в функции
        # build_phase (класс Game), будет содержать только back_to_type_choise,
        # в соостветствии с чем игроку будет отправлено сообщение о том, что у
        # него недостаточно средств для строительства
        if request_arg == 'back_to_type_choise':
            request = 'no_money_to_build'
            player_protocol.sendMessage(request.encode(encoding='utf-8'), True)
            return request_arg

        request = request + ':' + request_arg
        response = player_protocol.sendMessage(request.encode(encoding='utf-8'),
                                               True)

        return response