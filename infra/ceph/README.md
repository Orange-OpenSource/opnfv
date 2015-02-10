# Ceph Installation

---
## Intro
Ceph is used to build a storage system accross all machines

## Architecture
We consider the following architecture

    TODO: add schema (4 machines: ceph-admin, 3 ceph-nodes: opensteak9{2,3,4})

Networks:
```
192.168.0.0/24 is the cluster network (use for storage)
192.168.1.0/24 is the management network (use for admin task)
```


## Ceph-admin machine preparation

This is done on an Ubuntu 14.04 64b server

### Install ceph-deploy
```bash
wget -q -O- 'https://ceph.com/git/?p=ceph.git;a=blob_plain;f=keys/release.asc' | sudo apt-key add -
echo deb http://ceph.com/debian-firefly/ $(lsb_release -sc) main | sudo tee /etc/apt/sources.list.d/ceph.list
sudo apt-get update && sudo apt-get install ceph-deploy
```

### Install ntp
```bash
sudo apt-get install ntp
sudo service ntp restart
```

### Create a ceph user on each node (ceph-admin included)
```bash
sudo useradd -d /home/ceph -m ceph
sudo passwd ceph
```

Add sudo rights:
```bash
echo "ceph ALL = (root) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/ceph
sudo chmod 0440 /etc/sudoers.d/ceph
```

* *Note: if you think this can be a security treat, remove the ceph user from sudoers after installation is complete*

* *Note 2: the ceph documentation ask for this user: http://ceph.com/docs/master/rados/deployment/preflight-checklist/?highlight=sudoers*


### Add each node in hosts file (ceph-admin included)
```bash
sudo bash -c ' cat << EOF >> /etc/hosts
192.168.1.200 ceph-admin
192.168.1.92 opensteak92
192.168.1.93 opensteak93
192.168.1.94 opensteak94
EOF'
```

### Create and copy a passwordless ssh key to each node
```bash
ssh-keygen
ssh-copy-id ceph@ceph-admin
ssh-copy-id ceph@opensteak92
ssh-copy-id ceph@opensteak93
ssh-copy-id ceph@opensteak94
```

### Create a .ssh/config file to connect automatically
```bash
cat << EOF >> .ssh/config
Host ceph-admin
  Hostname ceph-admin
  User ceph
Host opensteak92
  Hostname opensteak92
  User ceph
Host opensteak93
  Hostname opensteak93
  User ceph
Host opensteak94
  Hostname opensteak94
  User ceph
EOF
```

## Ceph storage cluster
All these commands must be run inside the ceph-admin machine as a regular user

### Prepare folder
```bash
mkdir ceph-cluster
cd ceph-cluster/
```

### Deploy initial monitor on first node
```bash
ceph-deploy new opensteak92
```

### Configure ceph
We set default pool size to 2 and public/cluster networks:

```bash
cat << EOF >> ceph.conf
osd pool default size = 2
public network = 192.168.1.0/24
cluster network = 192.168.0.0/24
EOF
```

### Install ceph in all nodes
```bash
ceph-deploy --username ceph install ceph-admin opensteak92 opensteak93 opensteak94
```

### Create initial monitor and gather the keys
```bash
ceph-deploy --username ceph mon create-initial
```

### Create and add OSD
We will use hard disk (/dev/sdb) for storage: http://docs.ceph.com/docs/master/rados/deployment/ceph-deploy-osd/

```bash
ceph-deploy --username ceph osd create opensteak93:sdb
ceph-deploy --username ceph osd create opensteak94:sdb
```

### Prepare all nodes to administer the cluster
Prepare all nodes with a ceph.conf and ceph.client.admin.keyring keyring so that it can administer the cluster:

```bash
ceph-deploy admin ceph-admin opensteak92 opensteak93 opensteak94
sudo chmod +r /etc/ceph/ceph.client.admin.keyring
```

### Add a metadata server in first node
```bash
ceph-deploy--username ceph mds create opensteak92
```

## Extend
### Extend the OSD pool
We decided to extend OSD pool by adding the first node as well:

```bash
ceph-deploy --username ceph osd create opensteak92:sdb
```

### Extend the monitors
In the same spirit, extend the monitor by adding the two last nodes and check the status
```bash
ceph-deploy --username ceph mon create opensteak93 opensteak94
ceph quorum_status --format json-pretty
```

## Check status
```bash
ceph health
```

## Create a file system
Check osd pools:
```bash
ceph osd lspools
```

I you don't have data and metadata pools, create it:
```bash
ceph osd pool create cephfs_data 64
ceph osd pool create cephfs_metadata 64
```

Then enable filesystem on the cephfs_data pool:
```bash
ceph fs new cephfs cephfs_metadata cephfs_data
```

And check again:
```bash
ceph osd lspools
```

Should produce:
```bash
0 rbd,1 cephfs_data,2 cephfs_metadata,
```

You can check as well with:
```bash
$ ceph fs ls
name: cephfs, metadata pool: cephfs_metadata, data pools: [cephfs_data ]

$ ceph mds stat
e5: 1/1/1 up {0=opensteak92=up:active}
```

## Mount file system
For each node you want to mount ceph in **/mnt/cephfs/**, run:
```bash
ssh opensteak9x "cat /etc/ceph/ceph.client.admin.keyring |grep key|awk '{print \$3}'|sudo tee /etc/ceph/ceph.client.admin.key"

ssh opensteak9x "sudo mkdir /mnt/cephfs"

ssh opensteak9x "echo '192.168.1.92:6789:/ /mnt/cephfs ceph name=admin,secretfile=/etc/ceph/ceph.client.admin.key,noatime 0 2' | sudo tee --append /etc/fstab && sudo mount /mnt/cephfs"
```

This will add a line in fstab so the file system will automatically be mounted on boot.

## TODO

* create a python/bash script that will install & check that the cluster is well configured (do all of this automatically)
* create a conf file that will be used by the above script to describe the architecture?
