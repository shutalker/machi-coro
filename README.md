[![Build Status](https://travis-ci.org/shutalker/machi-coro.svg?branch=develop)](https://travis-ci.org/shutalker/machi-coro)

# Machi-coro
### Реализация популярной японской настолки
---
[Полные правила](https://hobbygames.ru/download/rules/Machi_Koro_rules-web_2015.pdf) и [Карты](http://tesera.ru/images/items/336041/machi%20koro.pdf)

#### Установка клиента:

    git clone https://github.com/shutalker/machi-coro

    cd ./machi-coro

    sudo apt install ./machicoroclient_version-release_arch.deb  # здесь надо указать текущую версию пакета

#### Запуск клиента:

    mc_gameclient.py -a 146.185.155.249 -p 9000

#### Удаление клиента:

    sudo apt remove machicoroclient


### Запуск клиента без установки пакета:

Примечание: для установки всех необходимых пакетов используйте систему управления пакетами,
имеющуюся в Вашей системе (apt, yum и др.). Здесь приводится пример установки пакетов
с помощью apt.

    sudo apt install python3.5 python3-all python3-setuptools python3-pip git

    mkdir ./machicoroclient

    cd ./machicoroclient

Здесь производится установка и активация виртуального окружения:

    python3 -m venv env

    . env/bin/activate

Перед выполнением следующей команды необходимо [cконфигурировать](https://git-scm.com/book/ru/v1/%D0%92%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-%D0%9F%D0%B5%D1%80%D0%B2%D0%BE%D0%BD%D0%B0%D1%87%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F-%D0%BD%D0%B0%D1%81%D1%82%D1%80%D0%BE%D0%B9%D0%BA%D0%B0-Git) git

    git clone https://github.com/shutalker/machi-coro


    cd ./machi-coro

    pip3 install -r requirements.txt

    export PYTHONPATH=`pwd`

    cd ./client

Запуск клиента:

    python mc_gameclient.py -a 146.185.155.249 -p 9000

Для деактивации виртуального окружения следует набрать:

    deactivate