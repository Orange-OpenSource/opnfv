# OpenSteak install with Foreman

## Pre-requisite

1 medium server installed with > ubuntu 14.04 connected to the admin network
1 controller server at least that will contain the Openstack VM

## Get the code and configure

* Install dependancies:

```
sudo aptitude install libvirt-bin git qemu-kvm genisoimage bridge-utils
sudo service libvirt-bin restart
```

* Get the code:

```
git clone https://github.com/Orange-OpenSource/opnfv.git
```

* Configure, check the config, and check again
Edit the file ```~/opnfv/infra/config/infra.yaml```

* Check again the config file...

## Prepare libvirt

This part will be added in the script in the future release
Set default pool for libvirt during the install not before

### Set the network

We need to set the admin interface on a bridge.

If this interface is eth0 with ip 192.168.1.4 and gateway 192.168.1.1,
and the default ip on the actual bridge (virbr0) is 192.168.122.1,
this is the lines you need to execute.

```
ubuntu@jumphost:~$ sudo ip a d 192.168.122.1/24 dev virbr0
ubuntu@jumphost:~$ sudo ip a a 192.168.1.4/24 dev virbr0
ubuntu@jumphost:~$ sudo ip a d 192.168.1.4/24 dev eth0 && sudo brctl addif virbr0 eth0
ubuntu@jumphost:~$ sudo ip r a default dev virbr0 via 192.168.1.1
```

Save the config, edit ```/etc/network/interfaces``` and set changed interfaces:
```
# Set up interfaces manually, avoiding conflicts with, e.g., network manager
iface eth0 inet manual
# Bridge setup
iface virbr0 inet static
        bridge_ports eth0
        address 192.168.1.4
        broadcast 192.168.1.255
        netmask 255.255.255.0
        gateway 192.168.1.1

```


### Issue #9
* Create the default_pool.xml file:

```
      <pool type="dir">
        <name>default</name>
        <target>
          <path>/var/lib/libvirt/images</path>
        </target>
      </pool>
```

* Create the pool

 ```sudo virsh pool-define default_pool.xml```

* Start and Set autostart

 ```
ubuntu@jumphost:~$ sudo virsh pool-start default
ubuntu@jumphost:~$ sudo virsh pool-autostart default
```

* Refresh and check

```
ubuntu@jumphost:~$ sudo virsh pool-refresh default
ubuntu@jumphost:~$ sudo virsh pool-list --all
```

### Issue #10

```
ubuntu@jumphost:~$ sudo wget -O /var/lib/libvirt/images/trusty-server-cloudimg-amd64-disk1.img http://cloud-images.ubuntu.com/trusty/current/trusty-server-cloudimg-amd64-disk1.img
```

## Install Foreman VM

```
ubuntu@jumphost:~$ cd opnfv/infra/
ubuntu@jumphost:~/opnfv/infra$ sudo python3 create_foreman.py
```

When done, you can check the creation process with:

```sudo tail -f /var/log/libvirt/qemu/foreman-serial.log```


## Configure Foreman

* Install python foreman api

```
ubuntu@jumphost:~/opnfv/infra$ sudo pip3 install foreman
```

* Configure Foreman

```
ubuntu@jumphost:~/opnfv/infra$ sudo python3 configure_foreman.py
```
