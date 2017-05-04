import unittest
from game_logic.player import Player
from card.sight_card import SightCard


class BuildEnterpriseTestCase(unittest.TestCase):

    '''
        TestCase'ы для методов строительства предприятий из класса Player
    '''

    def test_build_sight(self):

        '''
            Тестирование функции build_sight()
        '''

        start_bank_size = 3
        card_name = u'Вокзал'

        player = Player(start_bank_size)

        # атрибуты карты (будут храниться в бд и извлекаться из нее)
        card_props = {
            'name': card_name,
            'price': 2,
            'description': u'Вы можете бросить 1 или 2 кубика.',
            'effect_cost': (0, 0),
            'effect_name': 'railway_station'
        }

        bank_after_one_building = start_bank_size - card_props['price']
        sight_card = SightCard(card_props, player.id)
        player.sight_card_hand[card_name] = sight_card
        player.build_sight(card_name)

        # 1 ситуация: у игрока хватает средств на строительство
        self.assertEqual(player.sight_card_hand[card_name].is_built, True)
        self.assertEqual(player.bank, bank_after_one_building)
        self.assertEqual(player.built_sight_amount, 1)

        # 2 ситуация: у игрока не хватает средст на строительство
        player.built_sight_amount = 0
        player.sight_card_hand[card_name].is_built = False
        player.build_sight(card_name)
        self.assertEqual(player.sight_card_hand[card_name].is_built, False)
        self.assertEqual(player.bank, bank_after_one_building)
        self.assertEqual(player.built_sight_amount, 0)

    def test_build_enterprise(self):

        '''
            Теситрование функции build_enterprise()
        '''

        start_bank_size = 3
        card_name = u'Пшеница'
        card_in_heap_amount = 2
        built_enterprise_counter = 0

        player = Player(start_bank_size)

        # колода карт резерва
        card_heap = {card_name: card_in_heap_amount}

        # атрибуты карты (будут храниться в бд и извлекаться из нее)
        card_props = {
            'name': card_name,
            'profit_type': 'from_bank_anytime',
            'profit_margin': 1,
            'branch_type': 'food',
            'price': 1,
            'description': u'Возьмите 1 монету из банка. В ход любого игрока.',
            'effect_cost': (1, 1)
        }

        for _ in range(card_in_heap_amount + 2):
            if player.build_enterprise(card_props, card_heap) == 1:
                built_enterprise_counter += 1

        hand_card_amount = player.enterprise_card_hand[card_name].hand_card_amount
        bank_after_buildings = start_bank_size - built_enterprise_counter
        self.assertEqual(hand_card_amount, card_in_heap_amount)
        self.assertEqual(player.bank, bank_after_buildings)
        self.assertEqual(card_heap[card_name], 0)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BuildEnterpriseTestCase)
    unittest.TextTestRunner().run(suite)