from uuid import uuid4     #уникальный uuid для каждого игрока
from card_enterprise_class import EnterpriseCard


class Player:

    '''
       Класс игрока. В игре каждый игрок имеет стартовый НАБОР КАРТ,
       которые приносят ему доход, БАНК (монеты), позволяющий
       СТРОИТЬ новые ПРЕДПРИЯТИЯ. В СВОЙ ХОД игрок обязан БРОСИТЬ КУБИК
       (1 или 2, в зависимости от того, построена ли достопримечательноть
       "Вокзал"), с тем, чтобы сервер определил, какие карты в руке игрока
       принесут ему доход. Игроки могут получать доход не в свой ход -
       это определяется эффектом карт
    '''

    def __init__(self, start_bank_size):

        '''
           Создание и инициаллизация инстансов класса происходит на сервере при
           поключении очередного игрока
        '''

        self.id = uuid4()
        self.bank = start_bank_size

        # при создании инстанса создается пустой словарь карт предприятий
        # он дополняется (функция сервера) стартовым набором карт (2 карты)
        self.enterprise_card_hand = dict()

        # все достопримечательности хранятся в словаре отдельно от предприятий
        # это сделано для упрощения обработки "специальных эффектов" карт
        self.sight_card_hand = dict()

        # флаг: позволяет определить, кто сейчас бросает кубик (т.е. является
        # активным игроком)
        self.is_active = False

        # количество построенных достопримечательностей: игра заканчивается,
        # когда первый из игроков построит все достопримечательности
        self.built_sight_amount = 0

    def build_sight(self, sight_name):

        '''
           Постройка достопримечательностей. После постройки для игрока
           становятся доступными эффекты построенных достопримечательностей.

           sight_name - это тип (имя) достопримечательноси, которую игрок
           собирается построить. Это имя является ключом в словаре, по которому
           осуществляется доступ к карте
        '''

        if self.sight_card_hand[sight_name].is_built:

            # если достопримечательность уже построена

            return -1

        sight_price = self.sight_card_hand[sight_name].price

        if sight_price > self.bank:

            # если у игрока недостаточно денег для строительства предприятия,
            # то сервер, обработав данный код возврата, сообщит игроку об этом
            # и предложит (в цикле) либо выбрать другую постройку, либо вовсе
            # отказаться от строительства
            return 0

        self.bank -= sight_price
        self.sight_card_hand[sight_name].is_built = True
        self.built_sight_amount += 1

        return 1

    def build_enterprise(self, enterprise, card_heap):

        '''
           Постройка предприятий. В руке у игрока может быть несколько
           предприятий одного типа. В этом случае, при постройке еще одного
           предприятия, которое уже имеется у игрока, счетчик этого предприятия
           увеличивается на 1. Если строится новое предприятие, то оно сначала
           добавляется в руку, затем счетчик увеличивается на 1 (изначально 0)

           enterprise - cловарь, содержащий параметры карты предприятия,
           которое игрок собирается построить (см. базовый класс карт)
           card_heap - это "колода" карт резерва. Представляет собой словарь, в
           котором ключом является имя карты, а значением - количество таких
           карт, оставшихся в резерве и доступных для покупки и строительства.
           Этот словарь генерируется на сервере.
        '''

        enterprise_name = enterprise['name']
        enterprise_price = enterprise['price']

        if enterprise_price > self.bank:

            return 0

        # проверяем, сколько карт из резерва осталось в колоде
        card_in_heap_amount = card_heap[enterprise_name]

        if card_in_heap_amount < 1:

                return -1

        # если в руке игрока еще нет такой карты, то необходимо ее добавить
        # иначе, просто увеличить счетчик карт этого типа в руке
        if enterprise_name not in self.enterprise_card_hand:
            building_enterprise = EnterpriseCard(enterprise, self.id)
            self.enterprise_card_hand[enterprise_name] = building_enterprise

        self.enterprise_card_hand[enterprise_name].hand_card_amount += 1
        self.bank -= enterprise_price
        card_heap[enterprise_name] -= 1

        return 1

    def get_profit(self, dice_score, player_dict):

        '''
            Функция реализует фазу доходов в игре. Вызывается на каждом ходу
            для каждого игрока поочередно, начиная с активного игрока
            player_dict - словарь с игроками, где в качестве ключа выступает
            id игрока
        '''

        enterprise_card_list = list(self.enterprise_card_hand.values())

        for card in enterprise_card_list:
            if card.effect_cost[0] <= dice_score <= card.effect_cost[1]:
                self.bank += card.card_effect(player_dict)
