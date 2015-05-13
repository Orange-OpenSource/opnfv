#!/bin/bash

NAME=$3
hammer -u $1 -p $2 host delete --name $NAME
echo -e "update delete $NAME a\nupdate delete $NAME txt\nsend" | nsupdate -v -k /etc/bind/rndc.key -l
