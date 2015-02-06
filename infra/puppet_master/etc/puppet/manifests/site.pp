# Set exec path for all modules
Exec { path => '/usr/bin:/usr/sbin:/bin:/sbin' }

# Load classes defined in hieradata
hiera_include('classes')
