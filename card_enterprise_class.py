from card_base_class import BaseCard


class EnterpriseCard(BaseCard):

    '''
       Класс карт предприятий. Каждое предприятие в течение игры
       приносит владельцу доход, позволяющий строить другие предприятия
       и достопримечательности. Предприятия различаются по способу организации
       дохода (profit_type):
           1. Владелец получает доход из банка только в свой ход.
           2. Владелец получает доход из банка в ход любого игрока.
           3. Владелец получает доход из средств активного игрока.
           4. Владелец получает доход из средств соперников, но только
              в свой ход.
       Размер прибыли для каждой карты фиксирован (profit_margin).
       Предприятия также различаются по отраслям (branch_type): пищевая,
       деревообрабатывающая и т.д. Тип отрасли необходимо хранить, т.к.
       для некоторых типов предусмотрена возможность получать доход в двойном
       размере (эффект одной из карт достопримечательности)
    '''

    def __init__(self, card_properties, player_id):

        '''
           Словарь параметров карты, необходимый для ее инициаллизации
           содержит не только базовые атрибуты карты, но и параметры, присущие
           конкретному типу
        '''

        # инициаллизация атрибутов родительского класса
        super().__init__(card_properties, player_id)

        self.profit_type = card_properties['profit_type']
        self.branch_type = card_properties['branch_type']
        self.profit_margin = card_properties['profit_margin']

        # количество карт данного типа в руке каждого игрока (влияет на
        # суммарный доход от этого предприятия)
        self.hand_card_amount = 0

    def card_effect(self, player_dict):

        '''
            Функция-диспетчер. В зависимости от параметра profit_type
            эта функция будет возвращать результат вызова конкретного
            метода, реализующего один из способов организации дохода
            player_dict необходим для реализации эффектов, которые приносят
            доход из средств других игроков (необходимо корректировать значения
            из банков)
        '''

        profit_margin = 0
        profit_method_name = '_EnterpriseCard__card_effect_'
        profit_method_name += self.profit_type
        profit_method = getattr(self, profit_method_name)
        profit_margin = profit_method(player_dict)

        return profit_margin

    def __card_effect_from_bank_anytime(self, pass_arg):

        '''
            Получение дохода из банка в ход любого игрока
        '''

        profit_margin = self.profit_margin * self.hand_card_amount

        return profit_margin

    def __card_effect_from_bank(self, player_dict):

        '''
            Получение дохода из банка только в свой ход
        '''

        if player_dict[self.id].is_active:
            profit_margin = self.profit_margin * self.hand_card_amount

        return profit_margin

    def __card_effect_from_active_player(self, player_dict):

        '''
            Получение дохода из средств активного игрока
        '''

        profit_margin = 0

        for player_id in player_dict:

            # payer - плательщик, т.е. игрок, из чьих средств в данных момент
            # поступает доход игроку, у которого сработал данный эффект карты
            payer = player_dict[player_id]
            if player_id != self.id and payer.is_active:
                for _ in range(self.profit_margin * self.hand_card_amount):
                    if payer.bank > 0:
                        payer.bank -= 1
                        profit_margin += 1
                    else:
                        break

        return profit_margin

    def __card_effect_from_all_players(self, player_dict):

        '''
            Получение дохода из средств каждого игрока
        '''

        profit_margin = 0

        for player_id in player_dict:
            if player_id != self.id:
                payer = player_dict[player_id]
                for _ in range(self.profit_margin * self.hand_card_amount):
                    if payer.bank > 0:
                        payer.bank -= 1
                        profit_margin += 1
                    else:
                        break

        return profit_margin
