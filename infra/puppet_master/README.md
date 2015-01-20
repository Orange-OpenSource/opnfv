# Puppet Master

## Installation
    cd
    git clone https://github.com/davidblaisonneau-orange/opensteak.git
    cd opensteak/infra/puppet_master
    bash install-puppet-master.sh

This will 
* setup **puppet-master** on the machine from puppetlabs repo.
* configure your puppet master to use **environments**, **r10k** and **hiera**
* run r10k to populate your modules folder (check /etc/puppet/environments/)
* install vim syntax color for puppet modules

## Update modules
r10k will use modules from a **Puppetfile**. This file is manage through a github account on:
    https://github.com/arnaudmorinol/opensteak-r10k/tree/production

(the main branch is **production**)

If the Puppetfile is updated, you can update your puppet-master by running:
    opensteak-r10k-update

