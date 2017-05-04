DROP DATABASE IF EXISTS machi_coro;

CREATE DATABASE machi_coro
  DEFAULT CHARACTER SET utf8
  DEFAULT COLLATE utf8_general_ci;

CREATE TABLE IF NOT EXISTS `machi_coro`.`card` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(16) NOT NULL,
  `price` INT NOT NULL,
  `effect_cost` VARCHAR(8) NOT NULL,
  `description` VARCHAR(255) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name_UNIQUE` (`name` ASC))
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `machi_coro`.`enterprise` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `profit_type` VARCHAR(24) NOT NULL,
  `branch_type` VARCHAR(16) NULL,
  `profit_margin` INT NOT NULL,
  `amount` INT NOT NULL,
  `card_id` INT NOT NULL,
  PRIMARY KEY (`id`, `card_id`),
  CONSTRAINT `fk_enterprise_card1`
    FOREIGN KEY (`card_id`)
    REFERENCES `machi_coro`.`card` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS `machi_coro`.`sight` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `effect_name` VARCHAR(24) NOT NULL,
  `card_id` INT NOT NULL,
  PRIMARY KEY (`id`, `card_id`),
  CONSTRAINT `fk_sight_card1`
    FOREIGN KEY (`card_id`)
    REFERENCES `machi_coro`.`card` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Пшеница', 1, '1-1', 'Возьмите 1 монету из банка. В ЛЮБОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Ферма', 1, '2-2', 'Возьмите 1 монету из банка. В ЛЮБОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Лес', 3, '5-5', 'Возьмите 1 монету из банка. В ЛЮБОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Шахта', 6, '9-9', 'Возьмите 5 монет из банка. В ЛЮБОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Яблони', 3, '10-10', 'Возьмите 3 монеты из банка. В ЛЮБОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Пекарня', 1, '2-3', 'Возьмите 1 монету из банка. В СВОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Магазин', 2, '4-4', 'Возьмите 3 монеты из банка. В СВОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Сырзавод', 7, '7-7', 'Возьмите 5 монет из банка. В СВОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Овощебаза', 2, '11-12', 'Возьмите 8 монет из банка. В СВОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Кафе', 2, '3-3', 'Возьмите 1 монету у игрока, который бросил кубик.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Ресторан', 4, '9-11', 'Возьмите 2 монеты у игрока, который бросил кубик.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Стадион', 6, '6-6', 'Возьмите 2 монеты у каждого игрока. В СВОЙ ХОД.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Вокзал', 4, '0-0', 'Теперь Вы можете бросать 2 кубика.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Радио', 22, '0-0', 'Раз в ход Вы можете перебросить ОДИН кубик.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Порт', 16, '0-0', 'Выбросив на кубиках 10 очков, Вы можете добавить к результату 2 очка.');
INSERT INTO `machi_coro`.`card` VALUES (NULL, 'Аэропорт', 30, '0-0', 'Вы получите 10 монет, если откажетесь от строительства в свой ход.');

INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank_anytime', NULL, 1, 15, 1);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank_anytime', NULL, 1, 15, 2);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank_anytime', NULL, 1, 10, 3);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank_anytime', NULL, 5, 10,4);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank_anytime', NULL, 3, 10,5);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank', NULL, 1, 15, 6);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank', NULL, 3, 10, 7);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank', NULL, 5, 10, 8);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_bank', NULL, 8, 5, 9);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_active_player', NULL, 1, 10, 10);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_active_player', NULL, 2, 10, 11);
INSERT INTO `machi_coro`.`enterprise` VALUES (NULL, 'from_all_players', NULL, 2, 5, 12);

INSERT INTO `machi_coro`.`sight` VALUES (NULL, 'railway_station', 13);
INSERT INTO `machi_coro`.`sight` VALUES (NULL, 'radio_station', 14);
INSERT INTO `machi_coro`.`sight` VALUES (NULL, 'seaport', 15);
INSERT INTO `machi_coro`.`sight` VALUES (NULL, 'airport', 16);