#!/bin/bash

# Script name
PRGNAME=$(basename $0)

# Default variable values taken from export values if present
NAME="$NAME"
IP="$IP"
PASSWORD="$PASSWORD"
CREATEVM="$CREATEVM"
TARGETPOOL="$TARGETPOOL"

# Usage 
function usage() {

    cat << EOF >&1
Usage: $PRGNAME [options]

Description: This script will create config files for a VM in 
             current folder

Options:
    --help, -h
        Print this help and exit.
        
    --name, -n MACHINENAME
        Set the machine name.
        
    --ip, -i XXX.XXX.XXX
        Set the ip address of the machine.

    --password, -p PASSWORD
        Set the ssh password. Login is ubuntu.

    --targetpool, -t POOL
        Set the target pool to install the volume

    --createvm, -c
        Automatically create the VM after the configuration
        is done.
        
EOF
    echo -n '0'
    exit 0
}

# Command line argument parsing, the allowed arguments are
# alphabetically listed, keep it this way please.
LOPT="help,name:,ip:,password:,targetpool:,createvm"
SOPT="hn:i:p:t:c"

# Note that we use `"$@"' to let each command-line parameter expand to a
# separate word. The quotes around `$@' are essential!
# We need TEMP as the `eval set --' would nuke the return value of getopt.
TEMP=$(getopt --options=$SOPT --long $LOPT -n $PRGNAME -- "$@")

if [[ $? -ne 0 ]]; then
    echo "Error while parsing command line args. Exiting..." >&2
    exit 1
fi

# Note the quotes around `$TEMP': they are essential!
eval set -- "$TEMP"

while true; do
  case $1 in
    --help|-h)
                        usage
                        exit 0
                        ;;
    --name|-n)
                        NAME=$2; shift
                        ;;
    --ip|-i)
                        IP=$2; shift
                        ;;
    --targetpool|-t)
                        TARGETPOOL=$2; shift
                        ;;
    --password|-p)
                        PASSWORD=$2; shift
                        ;;
    --createvm|-c)
                        CREATEVM="y"
                        ;;
    --)
                        shift
                        break
                        ;;
    *)
                        echo "Unknow argument \"$1\"" >&2
                        exit 1
                        ;;
  esac
  shift
done

# Check args
if [ -z "$NAME" ]; then
    echo "Please provide a valid machine name. See --help option."  >&2
    exit 1
fi

if [ -z "$IP" ]; then
    echo "Please provide a valid ip address. See --help option."  >&2
    exit 1
fi

# If not target pool use ceph if available
if [ -z "$TARGETPOOL" ]; then
    if virsh pool-list | grep " ceph " > /dev/null; then
        TARGETPOOL='ceph'
        TARGETFOLDER='/mnt/cephfs'
    else
        TARGETPOOL='default'
        TARGETFOLDER='/var/lib/libvirt/images'
    fi
else
    if [ "$TARGETPOOL" = "ceph" ] && virsh pool-list | grep " ceph " > /dev/null; then
        TARGETFOLDER='/mnt/cephfs'
    elif [ "$TARGETPOOL" = "default" ] && virsh pool-list | grep " default " > /dev/null; then
        TARGETFOLDER='/var/lib/libvirt/images'
    else
        echo "Please provide a valid target pool. Available pools are listed in 'virsh pool-list'"  >&2
        exit 1
    fi
fi

if [ -z "$PASSWORD" ]; then
    echo "Please provide a valid ssh password. See --help option."  >&2
    exit 1
fi


echo "Creating VM configuration if folder '$NAME' with IP '$IP' and user ubuntu with password '$PASSWORD' in pool '$TARGETPOOL'"
if [ "Zy" = "Z$CREATEVM" ]; then
    echo "Will also create the VM."
fi
echo 
read -p "------ PRESS ANY KEY TO CONTINUE -------" -n 1 -r
echo
echo

mkdir $NAME
cd $NAME

cat << EOF > config.sh
export NAME='$NAME'
export IP='$IP'
export PASSWORD='$PASSWORD'
export TARGETPOOL='$TARGETPOOL'
EOF

cat <<EOF > meta-data
instance-id: $NAME;
network-interfaces: |
  auto lo
  iface lo inet loopback
  auto eth0
  iface eth0 inet static
    address $IP
    network 192.168.1.0
    netmask 255.255.255.0
    broadcast 192.168.1.255
    gateway 192.168.1.1
    dns-nameservers  192.168.1.201 8.8.8.8
    dns-search stack.opensteak.fr
local-hostname: $NAME
EOF
cat <<EOF > user-data
#cloud-config
password: $PASSWORD
chpasswd: { expire: False }
ssh_pwauth: True
dsmode: net
runcmd:
 - [ sh, -c, "ifdown eth0 && ifup eth0"]
 - [ sh, -c, "aptitude remove cloud-init -y"]
EOF
#dsmode: local

genisoimage -output $NAME-configuration.iso -volid cidata -joliet -rock user-data meta-data
sudo mv $NAME-configuration.iso $TARGETFOLDER/
virsh pool-refresh $TARGETPOOL 2>/dev/null
# virsh vol-list $TARGETPOOL

cat << EOF > $NAME.xml
<domain type='kvm'>
  <name>$NAME</name>
  <memory>1048576</memory>
  <currentMemory>1048576</currentMemory>
  <vcpu>2</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/><apic/><pae/>
  </features>
  <clock offset="utc"/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='$TARGETFOLDER/$NAME.img'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <disk type='file' device='disk'>
      <driver name='qemu' type='raw'/>
      <source file='$TARGETFOLDER/$NAME-configuration.iso'/>
      <target dev='vdb' bus='virtio'/>
    </disk>
    <input type='mouse' bus='ps2'/>
    <console type='pty'/>
    <memballoon model='virtio'/>
    <interface type='bridge'>
      <source bridge='br-adm'/>
      <virtualport type='openvswitch'>
      </virtualport>
      <target dev='vnet0'/>
      <model type='virtio'/>
      <alias name='net0'/>
    </interface>
  </devices>
</domain>
EOF

# Create the VM
if [ "Zy" = "Z$CREATEVM" ]; then
    export NAME="$NAME"
    export IP="$IP"
    export PASSWORD="$PASSWORD"
    export TARGETPOOL="$TARGETPOOL"
    create_vm.sh
fi
