#!/bin/bash

if [ "$TARGETPOOL" = "ceph" ] && virsh pool-list | grep " ceph " > /dev/null; then
    TARGETFOLDER='/mnt/cephfs'
elif [ "$TARGETPOOL" = "default" ] && virsh pool-list | grep " default " > /dev/null; then
    TARGETFOLDER='/var/lib/libvirt/images'
else
    echo "Please provide a valid target pool. Available pools are listed in 'virsh pool-list'"  >&2
    exit 1
fi

if virsh vol-list --pool "$TARGETPOOL" | grep $TARGETFOLDER/$NAME.img > /dev/null; then
    virsh vol-delete $TARGETFOLDER/$NAME.img
    if virsh vol-list --pool "$TARGETPOOL" | grep $TARGETFOLDER/template.img > /dev/null; then
        virsh vol-clone --pool $TARGETPOOL template.img $NAME.img
    else
        virsh vol-clone --pool $TARGETPOOL trusty-server-cloudimg-amd64-disk1.img $NAME.img
    fi
fi
virsh create $NAME.xml --console
