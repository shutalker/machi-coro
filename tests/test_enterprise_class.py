import unittest
from random import randint
from game_logic.player import Player
from card.enterprise_card import EnterpriseCard


class ProfitMethodsTestCase(unittest.TestCase):

    '''
       TestCase'ы для методов card_effect() из класса EnterpriseCard
    '''

    def test_from_bank_anytime(self):

        '''
           Тестирование функции card_effect_from_bank_anytime():
           получение дохода в ход любого игрока
        '''

        start_bank_size = 100
        card_name = u'Пшеница'

        # словарь игроков
        player_dict = dict()
        player = Player(start_bank_size)
        player_dict[player.id] = player

        # колода карт резерва
        card_heap = {card_name: 30}

        # атрибуты карты (будут храниться в бд и извлекаться из нее)
        card_props = {
            'name': card_name,
            'profit_type': 'from_bank_anytime',
            'profit_margin': 1,
            'branch_type': 'food',
            'price': 1,
            'description': u'Возьмите 1 монету из банка. В ход любого игрока.',
            'effect_cost': '1-1'
        }

        rand_card_amount = randint(1, 30)

        for _ in range(1, rand_card_amount):
            player.build_enterprise(card_props, card_heap)

        card_amount = player.enterprise_card_hand[card_name].hand_card_amount
        true_profit = card_amount * card_props['profit_margin']
        profit = player.enterprise_card_hand[card_name].card_effect(player_dict)

        self.assertEqual(profit, true_profit)

    def test_from_bank(self):

        '''
           Тестирование функции card_effect_from_bank():
           получение дохода из банка только в свой ход
        '''

        start_bank_size = 100
        card_name = u'Ферма'

        # словарь игроков
        player_dict = dict()
        player = Player(start_bank_size)
        player_dict[player.id] = player

        # колода карт резерва
        card_heap = {card_name: 30}

        # атрибуты карты (будут храниться в бд и извлекаться из нее)
        card_props = {
            'name': card_name,
            'profit_type': 'from_bank',
            'profit_margin': 2,
            'branch_type': 'fruit',
            'price': 1,
            'description': u'Возьмите 2 монеты из банка. В свой ход.',
            'effect_cost': '1-1'
        }

        rand_card_amount = randint(1, 30)

        for _ in range(1, rand_card_amount):
            player.build_enterprise(card_props, card_heap)

        card_amount = player.enterprise_card_hand[card_name].hand_card_amount
        true_profit = card_amount * card_props['profit_margin']

        # проверка реального получения дохода, когда игрок активный
        player.is_active = True
        profit = player.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, true_profit)

        # если игрок не является активным, то дохода он не получает
        player.is_active = False
        profit = player.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, 0)

    def test_from_active_player(self):

        '''
           Тестирование функции card_effect_from_active_player():
           получение дохода из средств активного игрока
        '''

        start_bank_size = 100
        card_name = u'Кафе'

        # словарь игроков
        player_dict = dict()

        # игрок, который должен получить доход от активного игрока
        profit_reciever = Player(start_bank_size)
        # игрок, из чьих средств начисляется доход
        active_player = Player(start_bank_size)
        player_dict[profit_reciever.id] = profit_reciever
        player_dict[active_player.id] = active_player

        # колода карт резерва
        card_heap = {card_name: 30}

        # атрибуты карты (будут храниться в бд и извлекаться из нее)
        card_props = {
            'name': card_name,
            'profit_type': 'from_active_player',
            'profit_margin': 3,
            'branch_type': 'cafe',
            'price': 1,
            'description': u'Возьмите 3 монеты у активного игрока',
            'effect_cost': '1-1'
        }

        rand_card_amount = randint(1, 30)

        for _ in range(1, rand_card_amount):
            profit_reciever.build_enterprise(card_props, card_heap)

        card_amount = profit_reciever.enterprise_card_hand[card_name].hand_card_amount
        true_profit = card_amount * card_props['profit_margin']

        # 1 ситуация: active_player действитльно активный, размера его банка
        # достаточно, чтобы покрыть весь доход (максимум - 90 монет)
        active_player.is_active = True
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, true_profit)

        # 2 ситуация: active_player в действительности не активный, т.е. доход
        # с него не соберется
        active_player.is_active = False
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, 0)

        # 3 ситуация: active_player - активный, но его банка недостаточно,
        # чтобы целиком покрыть доход
        active_player.is_active = True
        active_player.bank = 2
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, 2)

        # 4 ситуация: profit_reciever - активный игрок. В этом случае доход
        # самому себе не начисляется
        profit_reciever.is_active = True
        active_player.is_active = False
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, 0)

    def test_from_all_players(self):

        '''
           Тестирование функции card_effect_from_all_players():
           получение дохода из средств всех остальных игроков только в свой ход
        '''

        start_bank_size = 100
        card_name = u'Стадион'
        player_amount = 4

        # словарь игроков
        player_dict = dict()

        # игрок, который должен получить доход от активного игрока
        profit_reciever = Player(start_bank_size)
        player_dict[profit_reciever.id] = profit_reciever

        # игроки, из чьих средств начисляется доход
        for _ in range(player_amount):
            player = Player(start_bank_size)
            player_dict[player.id] = player

        # колода карт резерва
        card_heap = {card_name: 30}

        # атрибуты карты (будут храниться в бд и извлекаться из нее)
        card_props = {
            'name': card_name,
            'profit_type': 'from_all_players',
            'profit_margin': 2,
            'branch_type': 'special',
            'price': 1,
            'description': u'Возьмите 2 монеты у остальных игроков. В свой ход.',
            'effect_cost': '1-1'
        }

        rand_card_amount = randint(1, 30)

        for _ in range(1, rand_card_amount):
            profit_reciever.build_enterprise(card_props, card_heap)

        card_amount = profit_reciever.enterprise_card_hand[card_name].hand_card_amount
        true_profit = player_amount * card_amount * card_props['profit_margin']

        # 1 ситуация: доход нормально собирается со всех игроков
        profit_reciever.is_active = True
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, true_profit)

        # 2 ситуация: игрок, получающий доход, не является активным
        profit_reciever.is_active = False
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, 0)

        # 3 ситуация: доход собирается не в полном количестве
        profit_reciever.is_active = True
        true_profit = 4
        for player_id in player_dict:
            player_dict[player_id].bank = 1
        profit = profit_reciever.enterprise_card_hand[card_name].card_effect(player_dict)
        self.assertEqual(profit, true_profit)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProfitMethodsTestCase)
    unittest.TextTestRunner().run(suite)
