#!/bin/bash

if [ "$#" -ne 1 ] ; then
    echo "Usage: $0 'server/client' (choose one in dependence of what you need to install)"
    exit 1
fi

requires="python3 python3-pip sed"
if [ "$1" = "server" ] ; then
    requires="$requires mysql-server"
elif [ "$1" != "client" ] ; then
    echo "Unknown argument: $1"
    exit 2
fi

for package in $requires
do
    status=`dpkg -s $package | grep "Status"`
    if [ -z "$status" ] ; then
        installdir=$(dirname $0)
        . "${installdir}/dependences/setup_$package.sh"
        if [ "$?" -ne 0 ] ; then
            echo "Setup package $package error"
            exit 3
        fi
    fi
done

exit 0