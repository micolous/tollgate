********************
Deploying on fedora
********************

Before you start
================

* You must have a computer with two network interfaces - One to the internet, the other to your LAN. 
* You must have `rpmfusion-free`_ enabled.
* You must be running Fedora 16 or higher.

Installing the software
=======================

Add the `tollgate repository`_, or grab the rpms manually.
Install tollgate by running::

        yum install tollgate

* All docs and examples are provided in the tollgate rpm. They can be found in ``/usr/share/doc/tollgate/``

Core network
============

We can setup the network either with ``DNSMASQ`` or ``ISC-DHCP`` and ``BIND9``. This will document how to install ``ISC-DHCP`` and ``BIND9``. 

Install the packages::

        yum install dhcp bind

Setup your LAN facing network device with a static IP address. There is an example of this in ``example/fedora/ifcfg-lan``. 

Next, we setup ``ISC-DHCP``. This will provide DHCP addresses to your LAN network. Make sure you get this right, else you will have a DHCP conflict on your Internet side. There is an example config in ``example/dhcpd.conf``.

Before you can start DHCP, you must create the rndc key that will be shared with named. Run the command::

        rndc-confgen -a -r keyboard -b 256

Now ``ISC-DHCP`` can be started::

        systemctl enable dhcpd.service
        systemctl start dhcpd.service

Check ``systemctl status dhcpd.service`` and ``/var/log/messages`` if you encounter issues. 

Next named.conf needs to be configured. There is an example of this in ``example/fedora/named.conf``. This is a modification of the default named.conf.

Additionally, you must configure the forwards and reverse zones to match for ``ISC-DHCP``. There are example zones in ``example/fedora/named/``. These should go into ``/var/named/dynamic/``.

Now ``BIND9`` can be started::
        
        systemctl enable 
        systemctl start 




.. _rpmfusion-free: http://rpmfusion.org/Configuration
.. _tollgate repository: http://repo.tollgate.org.au/fedora/

