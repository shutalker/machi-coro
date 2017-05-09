from twisted.protocols import basic


class GameClientIO(basic.LineReceiver):

    delimiter = '\n'.encode('utf-8')

    def __init__(self, *args, **kwargs):

        super(GameClientIO, self).__init__(*args, **kwargs)

        self.gameProtocol = None
        self.quit_flag = False
        self.request_from_server = False
        self.request_type = ''
        self.request_desc = ''
        self.request_arg = None

    def connectionMade(self):
        self.transport.write('>>> '.encode('utf-8'))

    def lineReceived(self, line):
        line = line.decode('utf-8').strip()

        if not line:
            if self.request_from_server:
                self.transport.write('==> '.encode('utf-8'))
            else:
                self.transport.write('>>> '.encode('utf-8'))

            return

        # обработка ответа клиента на запрос сервера
        if self.request_from_server:
            request_name = 'process_' + self.request_type
            request_handler = getattr(self, request_name)

            response = request_handler(line, self.request_arg)
            if response == None:

                return

            self.request_from_server = False
            self.request_type = ''
            self.request_desc = ''
            self.request_arg = None

            # если ответ требуется отослать на сервер, то respone не является
            # пустой строкой
            if response != '':
                self.gameProtocol.sendMessage(response.encode('utf-8'))

            self.print_message('')

            return

        # парсинг команды от клиента
        command_parts = line.strip().split()
        command = 'do_' + command_parts[0].lower()
        command_args = command_parts[1:]
        try:
            command_handler = getattr(self, command)
        except AttributeError as e:
            error_message = "Ошибка: команда не найдена "
            error_message += "(наберите 'help', чтобы узнать список "
            error_message += "доступных команд)"
            self.sendLine(error_message.encode('utf-8'))
            self.transport.write('>>> '.encode('utf-8'))

            return
        else:
            command_handler(*command_args)

        if not self.quit_flag:
            self.transport.write('>>> '.encode('utf-8'))

    def connectionLost(self, reason):
        print('')

    def do_help(self, command=None):

        '''help [command]: список команд или описание указанной команды
                            (если указано название команды)'''

        if command:
            command_description = getattr(self, 'do_' + command).__doc__
            self.sendLine(command_description.encode())
        else:
            commands = [cmd[3:] for cmd in dir(self) if cmd.startswith('do_')]
            valid_commands = 'Доступные команды: ' + ' '.join(commands)
            self.sendLine(valid_commands.encode('utf-8'))

    def do_rules(self):

        '''rules: правила игры'''

        self.sendLine('Тут когда-нибудь будут правила...'.encode('utf-8'))

    def do_card(self, card_name):

        '''card [name]: список с названиями всех карт игры или описание
                        конкретной карты (если указано имя карты)'''

    def do_quit(self):

        '''quit: выход из игры'''

        self.quit_flag = True
        self.stopProducing()
        self.gameProtocol.sendClose()

    def print_message(self, message):

        '''
            Отображение сообщений от сервера или генерируемых в ходе
            обработки запроса
        '''

        self.transport.write('\r'.encode('utf-8'))
        self.sendLine(message.encode('utf-8'))

        if self.request_from_server:
            self.transport.write('==> '.encode('utf-8'))
        else:
            self.transport.write('>>> '.encode('utf-8'))

    def process_server_request(self, *args):

        '''
            Обработка запросов от сервера
        '''

        server_requests = {
            'yn_request' : {
                               'reroll_dice_request' : 'Хотите ли Вы перебросить кубик ("y"/"n")?',
                               'increase_dice_score_request' : 'Вы выбросили 10 очков. Желаете ли Вы увеличить это число на 2 ("y"/"n")?',
                           },

            '12_request' : {
                               'dice_amount_request' : 'Выберите количество кубиков для броска ("1"/"2"):',
                               'dice_idx_to_reroll_request' : 'Какой кубик Вы желаете перебросить ("1"/"2")?'
                           },

            'noreply_request' : {
                                    'profit_request' : '',
                                    'bank_loss_request' : '',
                                    'no_money_to_build' : 'У Вас недостаточно средств, чтобы строить предприятия данного типа!',
                                    'profit_from_no_build_request' : 'Вы получаете 10 монет за отказ от строительства!'
                                },

            'list_choise_request' : {
                                        'build_request' : 'Что Вы желаете построить на этом ходу (выберите номер строки)?',
                                        'build_choise_request' : 'Выберите предприятие для постройки (укажите номер строки):'
                                    }
        }

        self.request_from_server = True
        request = args[0]

        for request_block_key in server_requests:
            request_block = server_requests[request_block_key]
            if request in request_block:
                self.request_type = request_block_key

                break

        self.request_desc = server_requests[self.request_type][request]

        if len(args) > 1:
            self.request_arg = args[1]
        else:
            self.request_arg = None

        if self.request_type == 'list_choise_request':
            choises = self.request_arg.split(sep='+')
            for choise_idx in range(len(choises) - 1):
                self.request_desc += '\r\n' + str(choise_idx + 1) + '.' + \
                                     choises[choise_idx]
            if choises[-1] == 'build_denied':
                self.request_desc += '\r\n' + str(len(choises)) + '.' + \
                                     'Отказаться от строительства'
            elif choises[-1] == 'back_to_type_choise':
                self.request_desc += '\r\n' + str(len(choises)) + '.' + \
                                     'Возврат к выбору типа предприятия'

        self.print_message(self.request_desc)

    def process_12_request(self, choise, arg):

        '''
            Обработка запросов с выбором типа "1/2"
        '''

        correct_response = ['1', '2']

        if not (choise in correct_response):
            self.print_message('Ошибка выбора: укажите число "1" или "2"')
            self.print_message(self.request_desc)

            response = None
        else:
            response = choise

        return response

    def process_yn_request(self, choise, arg):

        '''
            Обработка запросов с выбором типа "y/n"
        '''

        correct_response = ['y', 'yes', 'n', 'no']

        if not (choise in correct_response):
            self.print_message('Ошибка выбора: укажите ("y" или "n")')
            self.print_message(self.request_desc)

            response = None
        else:
            if choise in  correct_response[:2]:
                response = 'accept'
            else:
                response = 'decline'

        return response

    def process_noreply_request(self, choise, arg):

        '''
            Обработка запросов, не требующих ответа
        '''

        if arg:
            self.print_message(arg)

        response = ''

    def process_list_choise_request(self, choise, arg):

        choises = arg.split(sep='+')
        choise_idx = int(choise) - 1

        if 0 <= choise_idx <= (len(choises) - 1):
            response = choises[choise_idx]
        else:
            self.print_message('Ошибка выбора: укажите номер строки варианта')
            self.print_message(self.request_desc)
            response = None

        return response