node /^glance.*$/ {
    include opensteak::ceph-client-glance
    include opensteak::glance
}
