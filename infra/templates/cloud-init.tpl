#cloud-config
#############################################
# OPENSTEAK VM '%fqdn'
#############################################
password: %password
chpasswd: { expire: False }
ssh_pwauth: True
dsmode: net
manage_etc_hosts: True
fqdn: %fqdn
#############################################
# FIRST BOOT COMMAND
# - reload main interface
# - install puppet from puppetlabs
# - remove cloud-init
#############################################
write_files:
-  encoding: b64
   path: /tmp/puppet.conf
   permissions: '0640'
   owner: root:root
   content: %puppet_conf_content
runcmd:
 - [ sh, -c, "apt-get -y update"]
 - [ sh, -c, "apt-get -y install puppet"]
 - [ sh, -c, "mv /etc/puppet/puppet.conf /etc/puppet/puppet.conf.old"]
 - [ sh, -c, "mv /tmp/puppet.conf /etc/puppet/puppet.conf"]
 - [ sh, -c, "service puppet restart"]
 - [ sh, -c, "puppet agent --enable"]
 - [ sh, -c, "puppet agent -t -v"]
 - [ sh, -c, "/usr/bin/wget --quiet --output-document=/dev/null --no-check-certificate %foremanurlbuilt"]
 - [ sh, -c, "dhclient -v"]
ssh_authorized_keys:
%sshauthkeys
#############################################
# FINAL MESSAGE AT END OF BOOT
#############################################
final_message: "The system '%fqdn' is finally up, after $UPTIME seconds"
