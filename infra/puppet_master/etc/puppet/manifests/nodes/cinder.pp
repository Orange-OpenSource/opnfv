node /^cinder.*$/ {
    include opensteak::ceph-client-cinder
    include opensteak::cinder
}
