#!/bin/bash

# Install puppet master
echo "* Install puppet master"
wget -q https://apt.puppetlabs.com/puppetlabs-release-trusty.deb
sudo dpkg -i puppetlabs-release-trusty.deb >/dev/null
sudo apt-get update >/dev/null
sudo apt-get -y install puppetmaster >/dev/null

# Get Puppet Conf
echo "* Push puppet conf"
sudo wget -q -O /etc/puppet/puppet.conf https://raw.githubusercontent.com/davidblaisonneau-orange/opensteak/master/infra/puppet_master/puppet.conf

# Get Hiera Conf
echo "* Push Hiera conf"
sudo wget -q -O /etc/puppet/hiera.yaml https://raw.githubusercontent.com/davidblaisonneau-orange/opensteak/master/infra/puppet_master/hiera.yaml
sudo rm /etc/hiera.yaml
sudo ln -s /etc/puppet/hiera.yaml /etc/hiera.yaml

# Install and config r10k
echo "* Install R10k"
sudo gem install -q r10k > /dev/null
sudo wget -q -O /etc/r10k.yaml https://raw.githubusercontent.com/davidblaisonneau-orange/opensteak/master/infra/puppet_master/r10k.yaml

echo "* Deploy R10k"
sudo r10k deploy environment -pv

# Install VIM puppet
echo "* Install VIM puppet"
mkdir -p ~/.vim/autoload ~/.vim/bundle
curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim
cat <<EOF > ~/.vimrc
execute pathogen#infect()
syntax on
filetype plugin indent on
EOF
sudo apt-get -y install git >/dev/null
cd ~/.vim/bundle
git clone https://github.com/rodjek/vim-puppet.git > /dev/null
