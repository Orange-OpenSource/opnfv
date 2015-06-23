#!/bin/sh
# -*- coding: utf-8 -*-
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Authors:
# @author: David Blaisonneau <david.blaisonneau@orange.com>
# @author: Arnaud Morin <arnaud1.morin@orange.com>

### Set vars
NAME="${name}"
DOMAIN="${domain}"
DATEE=$$(date +%F-%Hh%M)
IP="${ip}"
DHCP_RANGE="${dhcprange}"
REVERSE_DNS="${reversedns}"
DNS_FORWARDER="${dns}"
ADMIN="${admin}"
PASSWORD="${password}"

### Set correct env
#dpkg-reconfigure locales
export LC_CTYPE=en_US.UTF-8
export LANG=en_US.UTF-8
unset LC_ALL
umask 0022

### Check hostname is on the public interface
echo "* Ensure hostname point to external IP"
# Remove useless lines
perl -i -pe 's/^127.0.1.1.*\n$$//' /etc/hosts
perl -i -pe "s/^$${IP}.*\n$$//" /etc/hosts
# Append a line
echo "$${IP} $${NAME}.$${DOMAIN} $${NAME}" >> /etc/hosts

### Dependencies
echo "* Install dependencies"
apt-get -y install ca-certificates wget git isc-dhcp-server

### Set AppArmor
echo "* Set App armor"
cat /etc/apparmor.d/local/usr.sbin.dhcpd | grep '/etc/bind/rndc.key r,' >/dev/null
if [ $$? -eq 1 ] ; then
    echo "/etc/bind/rndc.key r," >> /etc/apparmor.d/local/usr.sbin.dhcpd
fi

### Prepare repos
echo "* Enable Puppet labs repo"
if [ "Z" = "Z$$(dpkg -l |grep 'ii  puppetlabs-release')" ] ; then
    wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
    dpkg -i puppetlabs-release-trusty.deb
    apt-get update
fi

# Install puppetmaster
echo "* Install puppetmaster"
if [ "Z" = "Z$$(dpkg -l |grep 'ii  puppetmaster')" ] ; then
    apt-get -y install puppetmaster
fi

# Enable the Foreman repo
echo "* Enable Foreman repo"
if [ ! -e /etc/apt/sources.list.d/foreman.list ] ; then
    echo "deb http://deb.theforeman.org/ trusty 1.8" > /etc/apt/sources.list.d/foreman.list
    echo "deb http://deb.theforeman.org/ plugins 1.8" >> /etc/apt/sources.list.d/foreman.list
    wget -q http://deb.theforeman.org/pubkey.gpg -O- | apt-key add -
    apt-get update
fi

### Install Foreman
echo "* Install foreman-installer"
if [ "Z" = "Z$$(dpkg -l |grep 'ii  foreman-installer')" ] ; then
    apt-get -y install foreman-installer
fi
if [ "Z" = "Z$$(gem list --local |grep rubyipmi)" ] ; then
    gem install -q rubyipmi
fi

### Execute foreman installer
echo "* Execute foreman installer"

foreman-installer \
 --foreman-admin-username="$$ADMIN" \
 --foreman-admin-password="$$PASSWORD" \
 --enable-foreman-plugin-templates \
 --enable-foreman-plugin-discovery \
 --foreman-plugin-discovery-install-images=true \
 --puppet-listen=true \
 --enable-foreman-compute-libvirt


foreman-installer \
 --foreman-admin-username="$$ADMIN" \
 --foreman-admin-password="$$PASSWORD" \
 --enable-foreman-plugin-templates \
 --enable-foreman-plugin-discovery \
 --foreman-plugin-discovery-install-images=true \
 --enable-foreman-compute-libvirt \
 --enable-foreman-proxy \
 --foreman-proxy-bmc=true \
 --foreman-proxy-tftp=true \
 --foreman-proxy-tftp-servername="$$IP" \
 --foreman-proxy-dhcp=true \
 --foreman-proxy-dhcp-interface="eth0" \
 --foreman-proxy-dhcp-gateway="$$IP" \
 --foreman-proxy-dhcp-range="$$DHCP_RANGE" \
 --foreman-proxy-dhcp-nameservers="$$IP" \
 --foreman-proxy-dns=true \
 --foreman-proxy-dns-interface="eth0" \
 --foreman-proxy-dns-zone="$$DOMAIN" \
 --foreman-proxy-dns-reverse="$$REVERSE_DNS" \
 --foreman-proxy-dns-forwarders="$$DNS_FORWARDER" \
 --foreman-proxy-foreman-base-url="https://localhost"

### Sync community templates for last ubuntu versions

echo "* Sync community templates for last ubuntu versions"
foreman-rake templates:sync

### Get and install OpenSteak files

echo "* Get OpenSteak repos"
if [ -d /usr/local/opensteak ] ; then
    cd /usr/local/opensteak
    git pull
else
    cd /usr/local/
    git clone https://github.com/Orange-OpenSource/opnfv.git -b foreman opensteak
fi
cd /usr/local/opensteak/infra/puppet_master

echo "* Set puppet auth"
echo "*.$$DOMAIN" > /etc/puppet/autosign.conf
if [ -e /etc/puppet/auth.conf ] ; then
  # Make a backup
  mv /etc/puppet/auth.conf /etc/puppet/auth.conf.$$DATEE
fi
cp etc/puppet/auth.conf /etc/puppet/auth.conf
perl -i -pe "s/__FOREMAN_HOST__/$${NAME}.$${DOMAIN}/" /etc/puppet/auth.conf

# Set Hiera Conf
echo "* Push Hiera conf into /etc/puppet/"
if [ -e /etc/puppet/hiera.yaml ] ; then
  # Make a backup
  mv /etc/puppet/hiera.yaml /etc/puppet/hiera.yaml.$$DATEE
fi
cp etc/puppet/hiera.yaml /etc/puppet/hiera.yaml
if [ -e /etc/hiera.yaml ] ; then
  rm /etc/hiera.yaml
fi
ln -s /etc/puppet/hiera.yaml /etc/hiera.yaml
cp -rf etc/puppet/hieradata /etc/puppet/
rename s/DOMAIN/$$DOMAIN/ /etc/puppet/hieradata/production/nodes/*.yaml
cp etc/puppet/manifests/site.pp /etc/puppet/manifests/site.pp
cp ../config/common.yaml /etc/puppet/hieradata/production/common.yaml
chgrp puppet /etc/puppet/hieradata/production/*.yaml

# Install and config r10k
echo "* Install and setup r10k"
if [ "Z" = "Z$$(gem list --local |grep r10k)" ] ; then
    gem install -q r10k
fi
if [ -e /etc/r10k.yaml ] ; then
  # Make a backup
  mv /etc/r10k.yaml /etc/r10k.yaml.$$DATEE
fi
cp etc/r10k.yaml /etc/r10k.yaml

# Install opensteak-r10k-update script
echo "* Install opensteak-r10k-update script into /usr/local/bin"
cp usr/local/bin/opensteak-r10k-update /usr/local/bin/opensteak-r10k-update
chmod +x /usr/local/bin/opensteak-r10k-update

echo "* Run R10k. You can re-run r10k by calling:"
echo "   opensteak-r10k-update"
opensteak-r10k-update

#### Install VIM puppet
echo "* Install VIM puppet"
if [ ! -d ~/.vim/autoload ] ; then
  mkdir -p ~/.vim/autoload
fi
if [ ! -d ~/.vim/bundle ] ; then
  mkdir -p ~/.vim/bundle
fi
curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim
cat <<EOF > ~/.vimrc
execute pathogen#infect()
syntax on
filetype plugin indent on
EOF
cd ~/.vim/bundle
if [ ! -d vim-puppet ] ; then
  git clone https://github.com/rodjek/vim-puppet.git > /dev/null
fi

### Gen SSH key for foreman
echo "* SSH Key"
cp /mnt/id_rsa /usr/share/foreman/.ssh/
cp /mnt/id_rsa.pub /usr/share/foreman/.ssh/
chown foreman:foreman /usr/share/foreman/.ssh/ -R

### Run puppet
puppet agent -t -v
