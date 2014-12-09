ovs-vsctl add-br br-int
ovs-vsctl add-br br-vm
ovs-vsctl add-port br-vm eth1
ovs-vsctl add-br br-adm
ovs-vsctl add-port br-adm eth0
