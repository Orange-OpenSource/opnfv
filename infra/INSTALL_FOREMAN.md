# Foreman install for opensteak

Installation for Ubuntu 14.04

## Install foreman

### Prepare repos

```
echo "deb http://deb.theforeman.org/ trusty 1.7" > /etc/apt/sources.list.d/foreman.list
echo "deb http://deb.theforeman.org/ plugins 1.7" >> /etc/apt/sources.list.d/foreman.list
wget -q http://deb.theforeman.org/pubkey.gpg -O- | apt-key add -
apt-get update && apt-get install foreman-installer
```

### Install Foreman

```
gem install rubyipmi
sudo foreman-installer \
 --enable-foreman-proxy\
 --enable-foreman-plugin-templates\
 --enable-foreman-plugin-discovery\
 --foreman-plugin-discovery-install-images=true\
 --enable-foreman-compute-libvirt\
 --foreman-proxy-bmc=true\
 --foreman-proxy-tftp=true\
 --foreman-proxy-tftp-servername=192.168.1.4\
 --foreman-proxy-dhcp=true\
 --foreman-proxy-dhcp-interface=eth0\
 --foreman-proxy-dhcp-gateway=192.168.1.4\
 --foreman-proxy-dhcp-range="192.168.1.10 192.168.1.150"\
 --foreman-proxy-dhcp-nameservers="192.168.1.4"\
 --foreman-proxy-dns=true\
 --foreman-proxy-dns-interface=eth0\
 --foreman-proxy-dns-zone=infra.opensteak.fr\
 --foreman-proxy-dns-reverse=1.168.192.in-addr.arpa\
 --foreman-proxy-dns-forwarders=8.8.8.8\
 --foreman-proxy-foreman-base-url=https://localhost
```

### Sync community templates for last ubuntu versions
```
foreman-rake templates:sync
```

### Set AppArmor

```
perl -i -pe 's!#include <local/usr.sbin.dhcpd>!include <local/usr.sbin.dhcpd>!' /etc/apparmor.d/usr.sbin.dhcpd
echo "/etc/bind/rndc.key r," >> /etc/apparmor.d/local/usr.sbin.dhcpd
service apparmor reload
```

### Gen SSH key for foreman

```
su foreman -s /bin/bash
ssh-keygen
exit
```

### Set templates

#### Preseed default
We need to update the default 'Preseed default' template:

##### Avoid interfaces to be overwritten by preseed

Seen on http://projects.theforeman.org/projects/foreman/wiki/Tips_&amp_Tricks#Generating-etcnetworkinterfaces

Replace last line:
```
-d-i preseed/late_command string wget -Y off <%= @static ? "'#{foreman_url('finish')}&static=true'" : foreman_url('finish') %> -O /target/tmp/finish.sh && in-target chmod +x /tmp/finish.sh && in-target /tmp/finish.sh
```
with:
```
+d-i preseed/late_command string wget -Y off <%= @static ? "'#{foreman_url('finish')}&static=true'" : foreman_url('finish') %> -O /target/tmp/finish.sh && in-target chmod +x /tmp/finish.sh && in-target /tmp/finish.sh && rm -f /usr/lib/finish-install.d/55netcfg-copy-config
```

##### Create default ubuntu user

In user setting section, replace:

```
d-i passwd passwd/make-user boolean false
user-setup-udeb passwd/make-user boolean false
```
with:
```
# The user's name and login.
d-i passwd/make-user boolean true
user-setup-udeb passwd/make-user boolean true
passwd passwd/user-fullname string ubuntu
passwd passwd/username string ubuntu
d-i passwd/user-password-crypted password <%= root_pass %>
d-i passwd/user-default-groups string ubuntu adm dialout cdrom floppy sudo audio dip video plugdev netdev
d-i user-setup/encrypt-home boolean false
user-setup-udeb user-setup/encrypt-home boolean false
```

### Set some global parameters
In the foreman admin settings:
* Set ignore_puppet_facts_for_provisioning to true (see http://projects.theforeman.org/issues/1861#note-2)
* Set safemode_render to false


## Install opensteak classes

### Install r10k
from opnfv/infra folder
```
gem install -q r10k
cp puppet_master/etc/r10k.yaml /etc/r10k.yaml
cp puppet_master/usr/local/bin/opensteak-r10k-update /usr/local/bin/opensteak-r10k-update
sed -i -r "s|__PATCHESFOLDER__|$(pwd)puppet_master/patches|" /usr/local/bin/opensteak-r10k-update
chmod +x /usr/local/bin/opensteak-r10k-update
```

### Run r10k

```
opensteak-r10k-update
```

## Apply puppet classes to foreman

### Set DHCP server
Apply puppet class ''opensteak::dhcp'' to foreman:

Set those parameter in foreman GUI for foreman server

```
  opensteak::dhcp:
    dnsdomain:
    - infra.opensteak.fr
    - storage.infra.opensteak.fr
    - vm.infra.opensteak.fr
    - 0.168.192.in-addr.arpa
    - 1.168.192.in-addr.arpa
    - 2.168.192.in-addr.arpa
    interfaces:
    - eth0
    - eth1
    - eth2
    pools:
      pools:
        infra.opensteak.fr:
          network: 192.168.1.0
          netmask: 255.255.255.0
          range: 192.168.1.20 192.168.1.170
          gateway: 192.168.1.1
        storage.infra.opensteak.fr:
          network: 192.168.0.0
          netmask: 255.255.255.0
          range: 192.168.0.20 192.168.0.170
        vm.infra.opensteak.fr:
          network: 192.168.2.0
          netmask: 255.255.255.0
          range: 192.168.2.20 192.168.2.170
```

### Prepare Bind server

TO BE COMPLETED

### Run puppet

Run puppet on foreman

```
puppet agent -t
```
