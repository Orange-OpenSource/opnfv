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

# Check if br-ex exist, add it if not
ovs-vsctl br-exists br-ex
if [ $? -ne 0 ]; then
    ovs-vsctl add-br br-ex
fi

## Ports
# Check if port em2 is in br-ex, add it if not
PORT=$(ovs-vsctl list-ports br-ex |egrep "^em2$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-ex em2
fi

# Check if port em3 is in br-adm, add it if not
PORT=$(ovs-vsctl list-ports br-adm |egrep "^em3$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-adm em3
fi

# Check if port em4 is in br-storage, add it if not
PORT=$(ovs-vsctl list-ports br-storage |egrep "^em4$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-storage em4
fi

# Check if port em5 is in br-vm, add it if not
PORT=$(ovs-vsctl list-ports br-vm |egrep "^em5$")
if [ "Z$PORT" = "Z" ]; then
    ovs-vsctl add-port br-vm em5
fi

