#!/bin/bash
virsh vol-delete /var/lib/libvirt/images/$NAME.img
virsh vol-clone --pool default trusty-server-cloudimg-amd64-disk1.img $NAME.img
virsh create $NAME.xml --console
