#!/bin/sh
# Example wrapper to allow dnsmasq to call dhcp_script in your tollgate
# project correctly.
cd /var/tollgate_site; ./manage.py dhcp_script $*

