from uuid import uuid4
from random import randint
from game_logic.player import Player
from game_logic.server_request_handler import ServerRequestHandler
from card.enterprise_card import EnterpriseCard
from card.sight_card import SightCard


class Game:

    def __init__(self, card_heap, card_props, start_bank_size=3):

        self.id = uuid4()
        self.status = 'WAIT'

        # ключ в словаре - id игрока, значение - объект Player
        self.players = dict()

        self.card_heap = card_heap
        self.card_properties = card_props
        self.start_bank_size = start_bank_size
        self.end_game_flag = False
        self.active_player_disconnected = False

        # инстанс обработчика запросов клиентам от сервера
        self.request_handler = ServerRequestHandler()

    def add_player(self, player_protocol):

        '''
            При подключении к серверу, игрок регистрируется в одном
            из инстансов класса Game: новом - если все остальные геймы
            заняты, или в последнем незанятом (status == 'WAIT')
        '''

        new_player = Player(self.start_bank_size)
        self.request_handler.peers[player_protocol.peer] = {
            'transport' : player_protocol,
            'player_id' : new_player.id
        }
        self.players[new_player.id] = new_player
        # request = 'player_name_request'
        # player_name = self.request_handler.send_request(new_player.id,
        #                                                 request)
        # if player_name != None:
        #    new_player.name = player_name

    def pop_player(self, player_peer):

        '''
            При потере соединения игрока с сервером первый исключается
            из инстанса класса Game, т.е. больше не участвует в игре
        '''
        player_id = self.request_handler.peers[player_peer]['player_id']
        if self.players[player_id].is_active:
            self.active_player_disconnected = True
        player_name = self.players[player_id].name
        self.players.pop(player_id)
        self.request_handler.peers.pop(player_peer)
        request = 'Игрок ' + player_name + ' покинул игру'
        self.request_handler.broadcast(request)

    def init_players_hands(self):

        '''
            Инициаллизация стартовых рук игроков картами предприятий (2 карты)
            и достопримечательностей (4 карты)
        '''

        enterprise_init_hand = list()
        sight_init_hand = list()

        enterprise_init_hand.append(self.card_properties['Пшеница'])
        enterprise_init_hand.append(self.card_properties['Пекарня'])
        sight_init_hand.append(self.card_properties['Вокзал'])
        sight_init_hand.append(self.card_properties['Радио'])
        sight_init_hand.append(self.card_properties['Порт'])
        sight_init_hand.append(self.card_properties['Аэропорт'])

        for player_id in self.players:
            player = self.players[player_id]

            for card_idx in range(len(enterprise_init_hand)):
                card = EnterpriseCard(enterprise_init_hand[card_idx], 
                                                 player.id)
                card.hand_card_amount += 1
                player.enterprise_card_hand[card.name] = card

            for card_idx in range(len(sight_init_hand)):
                card = SightCard(sight_init_hand[card_idx], player.id)
                player.sight_card_hand[card.name] = card

    def roll_dice(self, active_player):

        '''
            Функция реализует выбрасывание игроком кубиков с возможностью
            изменять результат броска в зависимости от построенных
            достопримечательностей
        '''

        # если у игрока построена достопримечатльность "Вокзал",
        # то у игра запрашивает количество кубиков для выбрасывания
        if active_player.sight_card_hand['Вокзал'].is_built:
            request = 'dice_amount_request'
            dice_amount = self.request_handler.send_request(active_player.id,
                                                            request)
        else:
            dice_amount = 1

        # активный игрок "бросает кубик(и)"
        dice_scores = []
        for dice_idx in range(dice_amount):
            dice_scores.append(randint(1, 6))

        # если у игрока построена достопримечательность "Радио",
        # то игра запрашивает у него перебрасывание одного кубика
        if active_player.sight_card_hand['Радио'].is_built:
            request = 'reroll_dice_request:' + str(dice_amount)
            dice_idx, result = self.request_handler.send_request(active_player.id,
                                                                 request)
            if dice_idx != None:
                dice_scores[dice_idx] = result

        for score in dice_scores:
            sum_dice_score = score

        # если у игрока построена достопримечательность "Порт",
        # то игра запрашивает у него увеличение выброшенных очков на 2,
        # но только в том случае, если игрок выбросил 10 очков
        if active_player.sight_card_hand['Порт'].is_built and sum_dice_score == 10:
            request = 'increase_dice_score_request'
            increase_value = self.request_handler.send_request(active_player.id,
                                                               request)
            sum_dice_score += increase_value

        return sum_dice_score

    def get_avaliable_enterprises(self, player):

        '''
            Получение списка доступных для постройки игроком предприятий
        '''

        player_bank = player.bank
        avaliable_enterprises = []

        for enterprise_name in self.card_heap:
            enterprise_amount = self.card_heap[enterprise_name]

            if enterprise_amount > 0:
                enterprise_price = self.card_properties[enterprise_name]['price']

                if player_bank >= enterprise_price:
                    avaliable_enterprises.append(enterprise_name)

        return avaliable_enterprises

    def get_avaliable_sights(self, player):

        '''
            Получение списка доступных для постройки игроком
            достопримечательностей
        '''

        player_bank = player.bank
        avaliable_sights = []

        for sight_name in player.sight_card_hand:
            sight = player.sight_card_hand[sight_name]

            if not sight.is_built and player_bank >= sight.price:
                avaliable_sights.append(sight.name)

        return avaliable_sights

    def profit_phase(self, player_list, active_player_idx, dice_score):

        '''
            Функция реализует фазу доходов в игре. Доход получает каждый игрок
            на каждом ходу. Первым на данном ходу доход получает активный игрок
        '''

        player_list_len = len(player_list)
        next_player_idx = active_player_idx

        # список банков всех игроков непосредственно после получения дохода.
        # Необходим, чтобы позже расчитать убытки игроков
        bank_after_profit = [0] * player_list_len

        for _ in range(player_list_len):
            player = player_list[next_player_idx]
            profit = player.get_profit(dice_score, self.players)

            # запоминаем банк игрока после получения дохода с тем,
            # чтобы потом вычислить убытки, которые он понесет из-за эффектов
            # карт других игроков
            bank_after_profit[next_player_idx] = player.bank

            request = 'profit_request:' + str(profit)
            self.request_handler.send_request(player.id, request)
            next_player_idx += 1
            if next_player_idx > (player_list_len - 1):
                next_player_idx = 0

        for idx, player in enumerate(player_list):
            bank_loss = bank_after_profit[idx] - player.bank
            request = 'bank_loss_request:' + str(bank_loss)
            self.request_handler.send_request(player.id, request)

    def building_phase(self, player):

        '''
            Функция реализует фазу строительства в игре. На этой фазе активный
            игрок имеет право построить 1 предприятие / достопримечательность
            или отказаться от строительства. Если игрок отказался от
            строительста и имеет построенную достопримечательность "Аэропорт",
            то он получает 10 монет дохода на этом ходу
        '''

        build_status = ''

        while build_status != 'build_successful':
            request = 'build_request'
            response = self.request_handler.send_request(player.id, request)

            if response == 'build_denied':
                if player.sight_card_hand['Аэропорт'].is_built:
                    request = 'profit_from_no_build_request'
                    self.request_handler.send_request(player.id, request)
                    player.bank += 10

                build_status = 'build_successful'
            else:
                # возвращается 'build_enterprise' или 'build_sight'
                request = 'build_choise_request:'

                # функции возвращают списки доступных для постройки предприятий
                # в виде строк с их названиями
                # игрок на клиентской стороне должен будет выбрать одно из них
                # для постройки или вернуться назад к выбору типа постройки
                if response == 'build_enterprise':
                    avaliable_buildings = self.get_avaliable_enterprises(player)
                elif response == 'build_sight':
                    avaliable_buildings = self.get_avaliable_sights(player)

                # запрос типа 'text+text+...+text+' будет парситься на стороне
                # клиента, причем последний символ '+' в строке нужен не просто
                # так: при вызове функции split в список последним элементом
                # запишется строка 'Возврат к выбору типа предприятий'
                for building in avaliable_buildings:
                    request += building + '+'

                request += 'Возврат к выбору типа предприятий'

                # сюда вернется либо название карты, либо back_to_type_choise
                build_status = self.request_handler.send_request(player.id,
                                                                 request)

                if build_status != 'back_to_type_choise':
                    if response == 'build_enterprise':
                        enterprise = self.card_properties[build_status]
                        player.build_enterprise(enterprise, self.card_heap)
                    elif response == 'build_sight':
                        sight = build_status
                        player.build_sight(sight)

                    build_status = 'build_successful'

    def start(self):

        '''
            В функции реализована основная логика игры
        '''

        self.status = 'PLAYING'
        self.init_players_hands()
        current_active_player_idx = -1
        print('Game ' + str(self.id) + ' has started')

        request = 'Игра началась! Приятной игры!'
        self.request_handler.broadcast(request)

        while not self.end_game_flag:
            # это делается на каждом ходу, поскольку игроки в процессе игры
            # могут отключаться от серверва, что приводит к корректировке
            # словарей и очередности хода
            turn_queue = list(self.players.values())
            turn_queue_len = len(turn_queue)

            # если игру покинули все игроки до ее логического завершения,
            # то гейм завершается
            if turn_queue_len < 1:
                break

            current_active_player_idx += 1

            if current_active_player_idx > (turn_queue_len - 1):
                current_active_player_idx = 0

            active_player = turn_queue[current_active_player_idx]
            active_player.is_active = True

            # разослать всем игрокам, какой игрок является активным
            request = 'Активный игрок: ' + str(active_player.name)
            self.request_handler.broadcast(request)

            request = 'active_player_request'
            self.request_handler.send_request(active_player.id, request)

            dice_score = self.roll_dice(active_player)

            # отправка результата броска кубика всем игрокам
            request = 'Игрок ' + str(active_player.name) + ' выбрасывает ' + \
                  str(dice_score) + ' очков!'
            self.request_handler.broadcast(request)

            # фаза доходов
            self.profit_phase(turn_queue, current_active_player_idx,
                              dice_score)

            # фаза строительства
            self.building_phase(active_player)

            active_player.is_active = False
            sights_to_build = len(active_player.sight_card_hand)

            if active_player.built_sight_amount == sights_to_build:
                request = 'ПОБЕДИТЕЛЬ - ' + active_player.name + '!'
                self.request_handler.broadcast(request)
                self.request_handler.close_all_connections()
                break


    def stop(self):

        self.end_game_flag = True