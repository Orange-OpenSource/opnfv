#!/bin/bash

# Be sure that we are running as root
# Test si user root
if [ "Z$USER" != "Zroot" ] ; then
    echo "This script must be run as root"
    exit 1
fi

# Install dependencies
apt-get install toto
