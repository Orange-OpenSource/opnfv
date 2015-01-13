#!/bin/bash

## Bridges
# Check if br-int exist, add it if not
ovs-vsctl br-exists br-int
if [ $? -ne 0 ]; then
    ovs-vsctl add-br br-int
fi

# Check if br-vm exist, add it if not
ovs-vsctl br-exists br-vm
if [ $? -ne 0 ]; then
    ovs-vsctl add-br br-vm
fi

# Check if br-adm exist, add it if not
ovs-vsctl br-exists br-adm
if [ $? -ne 0 ]; then
    ovs-vsctl add-br br-adm
fi

# Check if br-storage exist, add it if not
ovs-vsctl br-exists br-storage
if [ $? -ne 0 ]; then
    ovs-vsctl add-br br-storage
fi

## Ports
# Check if port eth1 is in br-vm, add it if not
PORT=$(ovs-vsctl list-ports br-vm |egrep "^eth1$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-vm eth1
fi

# Check if port eth0 is in br-adm, add it if not
PORT=$(ovs-vsctl list-ports br-adm |egrep "^eth0$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-adm eth0
fi

# Check if port eth0.600 is in br-storage, add it if not
PORT=$(ovs-vsctl list-ports br-storage |egrep "^eth0.600$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-storage eth0.600
fi

