#!/bin/bash

##--------------------------------------------------------
# Module Name : emerginov_services
# Version : 1.0.0
# 
# Software Name : Emerginov
# Version : 1.0
#
# Copyright © 2012 – 2013 France Télécom                                                                
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# or see the LICENSE file for more details.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#--------------------------------------------------------
# File Name   : emerginov_services/files/mgmt_scripts/functions.inc.sh
#
# Created     : Mon, 01 Oct 2012 13:38:00 +0200
# Authors     : Arnaud Morin <arnaud1.morin@orange.com>
#
# Description :
#   This file contains functions needed for bash scripts
#
#--------------------------------------------------------
# History     :
#
# 1.0.0 - 2012-10-01 : Release of the file
# 1.0.1 - 2013-09-09 : Add colored echo
##

#
# Function to check a numerical result
#
# @param REALRESULT is the result to be compared
# @param EXPECTEDRESULT is the expected result that is used to compare
# @param CRITICAL, if equal 1, script will exit if result is not equal
#        expected result
#
CHECKRESULT='function checkResult {
    if [ -z $3 ]; then
        echo "Calling checkResult without enough parameters, exiting... ";
        echo -n "1";
        exit 1;
    fi;
    REALRESULT=$1;
    EXPECTEDRESULT=$2;
    CRITICAL=$3;
    if [ "$REALRESULT" = "$EXPECTEDRESULT" ]; then 
        echo_green "[OK]";
    else
        echo_red "[ERROR]";
        if [ "$CRITICAL" = "1" ]; then
            echo_red " -- Critical error happened, exiting -- ";
            echo -n "1";
            exit 1;
        fi;
    fi;
};'


#
# Functions to print colored result on terminal 
#
# @param MSG to be printed
#
COLORED_ECHO='function echo_green {
    NORMAL="$(tput -Tlinux sgr0)";
    COLOR="$(tput -Tlinux bold ; tput -Tlinux setaf 2)";
    MSG="$1";
    echo "${COLOR}${MSG}${NORMAL}";
};

function echo_red {
    NORMAL="$(tput -Tlinux sgr0)";
    COLOR="$(tput -Tlinux bold ; tput -Tlinux setaf 1)";
    MSG="$1";
    echo "${COLOR}${MSG}${NORMAL}";
};

function echo_yellow {
    NORMAL="$(tput -Tlinux sgr0)";
    COLOR="$(tput -Tlinux bold ; tput -Tlinux setaf 3)";
    MSG="$1";
    echo "${COLOR}${MSG}${NORMAL}";
};'
