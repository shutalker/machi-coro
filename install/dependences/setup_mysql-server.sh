#!/bin/bash

check_exec_status() {
    if [ "$1" -ne 0 ] ; then
        exit $1
    fi
}


apt-get update
apt install mysql-server
check_exec_status "$?"
mysql_secure_installation
check_exec_status "$?"
status=systemctl status mysql.service | grep "Active" | awk '{print $2}'
if [ "$status" = "inactive" ] ; then
    systemctl mysql start
    check_exec_status "$?"
elif [ "$status" != "active" ] ; then
    exit 1
fi

exit 0