# Base infra install

## Introduction

blabla

## Installation

### Preflight

**TODO: upgrade this to install Ubuntu through PXE automatically**

For now, the installation is done over Ubuntu 14.04 64b servers that you should already have installed through your own mecanism (PXE, manual, at your convenience). 

### Clone this repo

```bash
cd /usr/local
git clone https://github.com/Orange-OpenSource/opnfv.git opensteak
```

### Install dependencies

As **root**, install the following packages:

```bash
apt-get install -y virtinst genisoimage curl qemu-system-x86 qemu-system-common qemu-keymaps ipxe-qemu
service libvirt-bin restart
```

### Libvirt default pool
Libvirt needs a pool to store virtual machines:

```bash
cd /usr/local/opensteak/infra/kvm/
virsh pool-create default_pool.xml
```
