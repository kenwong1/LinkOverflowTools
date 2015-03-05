#
# Puppet configuration file, for installing the following things on top of
# a base Centos 7.x x86_64 image:
#
# - Python 2.7.x
# - Django 1.7.x
#

#
# Defaults
#
Package { allow_virtual => true } # avoids annoying error messages.

#
# Install Python 2.7.x. Note that the base Centos Linux image already has this version, so
# this puppet rule will simply ensure that it's present. We don't want the version
# of Python changing underneath us.
#
package { 'python' :
  ensure => "2.7.5-16.el7"
}

#
# The additional EPEL repository is required so we can install PIP (via yum)
#
package { 'epel-release' :
  ensure => installed
}

#
# The Pip utility is required for installing Python packages, including Django.
#
package { 'python-pip' :
  ensure => installed,
  require => [ Package['python'], Package['epel-release'] ]
}

#
# By default, Pip is installed as "/bin/pip", yet Puppet looks for it as "/bin/pip-python".
# This is a frequently-cited problem with Redhat/Centos.
#
file { '/bin/pip-python' :
  ensure => 'link',
  target => '/bin/pip',
  require => [ Package['python-pip'] ]
}

#
# Install the Django Python package, version 1.7.3.
#
package { "django" :
  ensure => "1.7.3",
  provider => pip,
  require => [ Package['python-pip'], File['/bin/pip-python']]
}
