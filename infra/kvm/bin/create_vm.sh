#!/bin/bash

if [ "$TARGETPOOL" = "ceph" ] && virsh pool-list | grep " ceph " > /dev/null; then
    TARGETFOLDER='/mnt/cephfs'
elif [ "$TARGETPOOL" = "default" ] && virsh pool-list | grep " default " > /dev/null; then
    TARGETFOLDER='/var/lib/libvirt/images'
else
    echo "Please provide a valid target pool. Available pools are listed in 'virsh pool-list'"  >&2
    exit 1
fi

virsh vol-delete $TARGETFOLDER/$NAME.img
virsh vol-clone --pool $TARGETPOOL trusty-server-cloudimg-amd64-disk1.img $NAME.img
virsh create $NAME.xml --console
