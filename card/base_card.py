class BaseCard:

    '''
       Базовый класс карт. Инстансы этого класса содержат только основные
       атрибуты карты: id - для определения принадлежности карты к тому или
       иному игроку; name - название карты (ключ в словаре карт); description -
       словесное описание назначения карты; price - стоимость покупки карты
       (строительства предприятия/достопримечательности); effect_cost -
       очки срабатывания эффекта карты. Эти атрибуты присущи всем картам в игре
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

        # id необходимо, что бы иметь возможность узнать, является ли игрок
        # активным или нет на данном ходу. Т.е. все карты, принадлежащие одному
        # игроку, имеют тот же id, что и у игрока
        self.id = player_id
        self.name = card_properties['name']
        self.description = card_properties['description']
        self.price = card_properties['price']

        # эффект карты срабатывает только в том случае, если игрок выбросит
        # определенное количество очков (или количество очков в некотором
        # диапазоне чисел). Задается через tuple из 2 элементов
        effect_cost = card_properties['effect_cost'].split(sep='-')
        for idx, elem in enumerate(effect_cost):
            effect_cost[idx] = int(elem)

        self.effect_cost = tuple(effect_cost)

    def __bytes__(self):

        '''
            Перегрузка метода для вызова bytes(card_instance). Байтовая строка
            будет передаваться по сети от сервера клиенту с целью
            предоставления ему информации о картах
        '''

        separator = ':'
        card_info = self.name + separator
        card_info += self.description + separator
        card_info += str(self.price) + separator
        card_info += str(self.effect_cost[0]) + '-' + str(self.effect_cost[1])

        return bytes(card_info, encoding='utf-8')
