node /^keystone.*$/ {
    include opensteak::apt
    include opensteak::key
    include opensteak::keystone
}
