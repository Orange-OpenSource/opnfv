#!/bin/sh

### Set vars

DOMAIN="home"
OPENSTEAKFOLDER="opensteak"
OPENSTEAKROOT="/usr/local"
OPENSTEAKPATH="$OPENSTEAKROOT/$OPENSTEAKFOLDER"
DATEE=$(date +%F-%Hh%M)
IP=$(ip addr list eth0 |grep inet |cut -d' ' -f6|cut -d/ -f1 |head -n1)
DHCP_RANGE="'172.16.0.10 172.16.0.250'"
REVERSE_DNS="0.16.172"
DNS_FORWARDER="8.8.8.8"

### Prepare repos
echo "* Enable Puppet labs repo"
apt-get -y install ca-certificates wget
wget https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
dpkg -i puppetlabs-release-trusty.deb

# Enable the Foreman repo
echo "* Enable Foreman repo"
echo "deb http://deb.theforeman.org/ trusty 1.8" > /etc/apt/sources.list.d/foreman.list
echo "deb http://deb.theforeman.org/ plugins 1.8" >> /etc/apt/sources.list.d/foreman.list
wget -q http://deb.theforeman.org/pubkey.gpg -O- | apt-key add -

### Check hostname is on the public interface

echo "* Ensure hostname point to external IP"
perl -i -pe 's/^127.0.1.1.*\n$//' /etc/hosts
ip addr list eth0 |grep inet |cut -d' ' -f6|cut -d/ -f1| perl -pe "s/\$/\t\t$(hostname -f) $(hostname)/" >> /etc/hosts

### Install Foreman

echo "* Install foreman-installer"
apt-get update && apt-get -y install foreman-installer
gem install rubyipmi

echo "* Execute foreman installer"
sudo foreman-installer \
 --enable-foreman-proxy\
 --enable-foreman-plugin-templates\
 --enable-foreman-plugin-discovery\
 --foreman-plugin-discovery-install-images=true\
 --enable-foreman-compute-libvirt\
 --foreman-proxy-bmc=true\
 --foreman-proxy-tftp=true\
 --foreman-proxy-tftp-servername="$IP"\
 --foreman-proxy-dhcp=true\
 --foreman-proxy-dhcp-interface="eth0"\
 --foreman-proxy-dhcp-gateway="$IP"\
 --foreman-proxy-dhcp-range="$DHCP_RANGE"\
 --foreman-proxy-dhcp-nameservers="$IP"\
 --foreman-proxy-dns=true\
 --foreman-proxy-dns-interface="eth0"\
 --foreman-proxy-dns-zone="$DOMAIN"\
 --foreman-proxy-dns-reverse="$REVERSE_DNS.in-addr.arpa"\
 --foreman-proxy-dns-forwarders="$DNS_FORWARDER"\
 --foreman-proxy-foreman-base-url="https://localhost"

### Sync community templates for last ubuntu versions

echo "* Sync community templates for last ubuntu versions"
foreman-rake templates:sync


### Get and install OpenSteak files

echo "* Get OpenSteak repos"
apt-get -y install git
cd $OPENSTEAKROOT
git clone https://github.com/Orange-OpenSource/opnfv.git -b foreman opensteak
cd opensteak/infra/puppet_master

echo "* Set puppet auth"
echo "*.$DOMAIN" > /etc/puppet/autosign.conf
cp etc/puppet/auth.conf /etc/puppet/auth.conf
NET=$(hiera infra::network environment=production)
MASK=$(hiera infra::network_mask environment=production)
perl -i -pe "s/__NET__/$NET/" /etc/puppet/auth.conf
perl -i -pe "s/__MASK__/$MASK/" /etc/puppet/auth.conf

# Get Hiera Conf
echo "* Push Hiera conf into /etc/puppet/"
if [ -e /etc/puppet/hiera.yaml ] ; then
  # Make a backup
  mv /etc/puppet/hiera.yaml /etc/puppet/hiera.yaml.$DATEE
fi
cp etc/puppet/hiera.yaml /etc/puppet/hiera.yaml
if [ -e /etc/hiera.yaml ] ; then
  rm /etc/hiera.yaml
fi
ln -s /etc/puppet/hiera.yaml /etc/hiera.yaml
cp -rf etc/puppet/hieradata /etc/puppet/
rename s/DOMAIN/$DOMAIN/ /etc/puppet/hieradata/production/nodes/*.yaml
cp etc/puppet/manifests/site.pp /etc/puppet/manifests/site.pp
cp ../config/common.yaml /etc/puppet/hieradata/production/common.yaml
mv ../config/physical-nodes.yaml.tpl /etc/puppet/hieradata/production/physical-nodes.yaml
chgrp puppet /etc/puppet/hieradata/production/*.yaml

# Install and config r10k
echo "* Install and setup R10k"
gem install -q r10k
if [ -e /etc/r10k.yaml ] ; then
  # Make a backup
  mv /etc/r10k.yaml /etc/r10k.yaml.$DATEE
fi
cp etc/r10k.yaml /etc/r10k.yaml

# Install opensteak-r10k-update script
echo "* Install opensteak-r10k-update script into /usr/local/bin"
cp usr/local/bin/opensteak-r10k-update /usr/local/bin/opensteak-r10k-update
sed -i -r "s|__PATCHESFOLDER__|$(pwd)/patches|" /usr/local/bin/opensteak-r10k-update
chmod +x /usr/local/bin/opensteak-r10k-update

echo "* Run R10k. You can re-run r10k by calling:"
echo "   opensteak-r10k-update"
opensteak-r10k-update

# Restart puppetmaster
echo "* Restart puppetmaster"
service puppetmaster restart

# Install VIM puppet
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


### Set AppArmor

echo "* Set App armor"
perl -i -pe 's!#include <local/usr.sbin.dhcpd>!include <local/usr.sbin.dhcpd>!' /etc/apparmor.d/usr.sbin.dhcpd
echo "/etc/bind/rndc.key r," >> /etc/apparmor.d/local/usr.sbin.dhcpd

### Gen SSH key for foreman

echo "* Gen SSH Key"
su foreman -s /bin/bash
ssh-keygen
exit
