#!/bin/bash

check_exec_status() {
    if [ "$1" -ne 0 ] ; then
        exit $1
    fi
}

apt-get install software-properties-common
apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
ostype=`lsb_release -d | awk '{print tolower($2)}'`
codename=`lsb_release -c | awk '{print $2}'`
add-apt-repository "deb [arch=amd64,i386,ppc64el] http://mirror.mephi.ru/mariadb/repo/10.2/$ostype $codename main"

apt update
apt install mariadb-server
check_exec_status "$?"

unset ostype
unset codename

exit 0