# Installing on fedora #

## Before you start ##

You must have a computer with two network interfaces - One to the internet, the other to your LAN. 

You must have rpmfusion-free enabled.

You must be running Fedora 16 or higher.

## Installing the software ##

Add the tollgate repository, or grab the rpms manually.

Install tollgate by running:

yum install tollgate

## Core network ## 

We can setup the network either with DNSMASQ or ISC-DHCP and BIND9. This will document how to install ISC-DHCP and BIND9. 

yum install dhcp bind

Setup your LAN facing network device with a static IP address. There is an example of this in doc/example/fedora/ifcfg-lan. 

Next, we setup ISC-DHCP. This will provide DHCP addresses to your LAN network. Make sure you get this right, else you will have a DHCP conflict on your Internet side. There is an example config in doc/example/dhcpd.conf

Before you can start DHCP, you must create the rndc key that will be shared with named. Run the command:

rndc-confgen -a -r keyboard -b 256

Now ISC-DHCP can be started:

systemctl enable dhcpd.service
systemctl start dhcpd.service

Check systemctl status dhcpd.service and /var/log/messages if you encounter issues.


