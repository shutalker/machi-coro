#!/bin/bash

check_exec_status() {
    if [ "$1" -ne 0 ] ; then
        exit $1
    fi
}


apt-get update
apt install python3
check_exec_status "$?"
status=`dpkg -s $package | grep "Status"`
if [ -z "$status" ] ; then
    exit 1
fi

exit 0