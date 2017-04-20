class Card:

    '''
       Класс карт предприятий (базовый). Каждое предприятие в течение игры
       приносит владельцу доход, позволяющий строить другие предприятия
       и достопримечательности. Предприятия различаются по способу организации
       дохода (profit_type):
           1. Владелец получает доход из банка только в свой ход.
           2. Владелец получает доход из банка в ход любого игрока.
           3. Владелец получает доход из средств активного игрока.
           4. Владелец получаеь доход из средств соперников, но только
              в свой ход.
       Размер прибыли для каждой карты фиксирован (profit_margin).
       Предприятия также различаются по отраслям (branch_type): пищевая,
       деревообрабатывающая и т.д. Тип отрасли необходимо хранить, т.к.
       для некоторых типов предусмотрена возможность получать доход в двойном
       размере (эффект одной из карт достопримечательности)
    '''

    def __init__(self, card_properties, player_id):

        '''
           Создание инстансов карт будет происходить только по мере
           необходимости (например, при покупке игроком предприятия
           или при генерации стартовой руки игрока). При этом параметры карт
           будут извлекаться из базы данных и помещаться в словарь
           (card_properties) для дальнейшей его передачи в метод инициализации
           инстанса класса
        '''

        #id необходимо, что бы иметь возможность узнать, является ли игрок
        #активным или нет на данном ходу. Т.е. все карты, принадлежащие одному
        #игроку, имеют тот же id, что и у игрока
        self.id = player_id
        self.name = card_properties['name']
        self.profit_type = card_properties['profit_type']
        self.branch_type = card_properties['branch_type']
        self.profit_margin = card_properties['profit_matgin']
        self.description = card_properties['desc']
        self.price = card_properties['price']

        #эффект карты срабатывает только в том случае, если игрок выбросит
        #определенное количество очков (или количество очков в некотором
        #диапазоне чисел). Задается через tuple из 2 элементов
        self.effect_cost = card_properties['effect_cost']

        #количество карт данного типа в руке каждого игрока (влияет на
        #суммарный доход от этого предприятия)
        self.hand_card_amount = 0

    def __bytes__(self):

        '''
            Перегрузка метода для вызова bytes(card_instance). Байтовая строка
            будет передаваться по сети от сервера клиенту с целью предоставления
            ему информации о картах 
        '''

        separator = ':'
        card_info = self.name + separator
        card_info += self.description + separator
        card_info += self.profit_type + separator
        card_info += self.branch_type + separator
        card_info += str(self.profit_margin) + separator
        card_info += str(self.price)

        return bytes(card_info, encoding='utf-8')

    def card_effect(self, player_list, player_id):
       
        '''
            Функция-диспетчер. В зависимости от параметра profit_type
            эта функция будет возвращать результат вызова конкретного
            метода, реализующего один из способов организации дохода
        '''

        profit_margin = 0

        profit_methods = {
                            'from_bank_anytime': self._Card__card_effect_from_bank_anytime(player_list, player_id),
                            'from_bank': self._Card__card_effect_from_bank(player_list, player_id),
                            'from_active_player': self._Card__card_effect_from_active_player(player_list, player_id),
                            'from_all_players': self._Card__card_effect_from_all_players(player_list, player_id)
                         }
        profit_margin = profit_methods[self.profit_type](player_list, player_id)

        return profit_margin

    def __card_effect_from_bank_anytime(self, *args, **kwargs):

        '''
            Получение дохода из банка в ход любого игрока
        '''

        profit_margin = self.profit_margin * self.hand_card_amount

        return profit_margin

    def __card_effect_from_bank(self, player_list, player_id):

        '''
            Получение дохода из банка только в свой ход
        '''

        for player in player_list:
            if player.is_active and player.id == player_id:
                profit_margin = self.profit_margin * self.hand_card_amount
                break

        return profit_margin


    
    def __card_effect_from_active_player(self, player_list, player_id):

        '''
            Получение дохода из средтв активного игрока
        '''

        profit_margin = 0

        for player in player_list:
            if player.id != player_id and player.is_active:
                for _ in range(self.profit_margin * self.hand_card_amount):
                    if player.bank > 0:
                        player.bank -= 1
                        profit_margin += 1
                    else:
                        break

        return profit_margin

    def __card_effect_from_all_players(self, player_list, player_id):

        '''
            Получение дохода из средств каждого игрока
        '''

        profit_margin = 0

        for player in player_list:
            if player.id != player_id:
                for _ in range(self.profit_margin * self.hand_card_amount):
                    if player.bank > 0:
                        player.bank -= 1
                        profit_margin += 1
                    else:
                        break

        return profit_margin
