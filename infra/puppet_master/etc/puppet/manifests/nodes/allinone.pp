node /^allinone.*$/ {
    $ceph_enabled = hiera('ceph::enabled')
    
    include opensteak::nova-compute
    include opensteak::neutron-network
    
    if str2bool("$ceph_enabled" ){
        include opensteak::ceph-mon
        include opensteak::ceph-mds
        include opensteak::ceph-osd
        include opensteak::ceph-client-cinder
    }
}
