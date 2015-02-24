#!/bin/bash
PRGNAME=$(basename $0)
DOMAIN=$1
DATEE=$(date +%F-%Hh%M)

OPENSTEAKFOLDER="opensteak"
OPENSTEAKROOT="/usr/local"
OPENSTEAKPATH="$OPENSTEAKROOT/$OPENSTEAKFOLDER"

# Check if we are root
if [ "Z$USER" != "Zroot" ] ; then
  echo "You need to execute this script as root:"
  echo "sudo $PRGNAME"
  exit 1
fi

# Install puppet master
echo "* Install puppet master from puppet labs repo"
wget -q https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
dpkg -i puppetlabs-release-trusty.deb
apt-get update >/dev/null
apt-get -y install puppetmaster git >/dev/null

# Get files
echo "* Get Github files"
cd $OPENSTEAKROOT
git clone https://github.com/Orange-OpenSource/opnfv.git $OPENSTEAKFOLDER
cd $OPENSTEAKPATH/infra/puppet_master/

# Get Puppet Conf
echo "* Push puppet conf into /etc/puppet/"
if [ -e /etc/puppet/puppet.conf ] ; then
  # Make a backup
  mv /etc/puppet/puppet.conf /etc/puppet/puppet.conf.$DATEE
fi
cp etc/puppet/puppet.conf /etc/puppet/puppet.conf
echo "*.$DOMAIN" > /etc/puppet/autosign.conf
cp etc/puppet/auth.conf /etc/puppet/auth.conf

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
mv /tmp/hieradata /etc/puppet/hieradata/production/common.yaml
chgrp puppet /etc/puppet/hieradata/production/common.yaml

# Install and config r10k
echo "* Install R10k into /etc/r10k.yaml"
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

# Modify auth.conf template
NET=$(hiera infra::network environment=production)
MASK=$(hiera infra::network_mask environment=production)
perl -i -pe "s/__NET__/$NET/" /etc/puppet/auth.conf
perl -i -pe "s/__MASK__/$MASK/" /etc/puppet/auth.conf

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
