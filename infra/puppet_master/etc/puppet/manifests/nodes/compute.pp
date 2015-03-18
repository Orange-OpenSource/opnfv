node /^compute.*$/ {
    include opensteak::nova-compute
    include opensteak::neutron-compute
    include opensteak::ceph-mon
    include opensteak::ceph-mds
    include opensteak::ceph-osd
    include opensteak::ceph-client-cinder
}
