********************
Deploying on fedora
********************

Before you start
================

* You must have a computer with two network interfaces - One to the internet, the other to your LAN. 
* You must have `rpmfusion-free`_ enabled.
* You must be running Fedora 16 or higher. 
* You must have updated your system (``yum update``)
* You should run SELinux in permissive mode (``/etc/selinux/config``). While we have an SELinux policy package, at this time, it is not 100% guaranteed to work on a live system. If you feel brave, run in enforcing mode and notify us of encountered errors with attached AVC messages. 

Installing the software
=======================

Add the `tollgate repository`_, or grab the rpms manually.

You can install the tollgate repository by running::
        
        yum localinstall --nogpgcheck 'http://repo.tollgate.org.au/pub/fedora/f16/rpms/tollgate-repo-2.8.4_dev-4.fc16.noarch.rpm'

Install tollgate by running::

        yum install tollgate

* All docs and examples are provided in the tollgate rpm. They can be found in ``/usr/share/doc/tollgate/``

Core network
============

Make sure your networking is set to start on boot.::

        systemctl enable network.service
        systemctl start network.service

We can setup the network either with ``DNSMASQ`` or ``ISC-DHCP`` and ``BIND9``. This will document how to install ``ISC-DHCP`` and ``BIND9``. 

Install the packages::

        yum install dhcp bind bind-utils

Setup your LAN facing network device with a static IP address. There is an example of this in ``example/fedora/ifcfg-lan``, and the file you want to edit will be ``/etc/sysconfig/network-scripts/ifcfg-DEVICENAME``.

Additionally, ensure that your internet facing device is set to ``ONBOOT="yes"`` 
		
Once configured run.::

        ifup DEVICENAME

Next, we setup ``ISC-DHCP``. This will provide DHCP addresses to your LAN network. Make sure you get this right, else you will have a DHCP conflict on your Internet side. There is an example config in ``example/fedora/dhcpd.conf``.

Before you can start DHCP, you must create the rndc key that will be shared with named. Run the command::

        rndc-confgen -a -r keyboard -b 256
        chown named:named /etc/rndc.key 

Now ``ISC-DHCP`` can be started::

        systemctl enable dhcpd.service
        systemctl start dhcpd.service

Check ``systemctl status dhcpd.service`` and ``/var/log/messages`` if you encounter issues. 

Next named.conf needs to be configured. There is an example of this in ``example/fedora/named.conf``. This is a modification of the default named.conf.

Additionally, you must configure the forwards and reverse zones to match for ``ISC-DHCP``. There are example zones in ``example/fedora/named/``. These should go into ``/var/named/dynamic/``.

Please note, we have provided a zone for ``conntest.nintendowifi.net``. This is also aided by a component in HTTPD (Documented later). This is to allow the Nintendo DS, Nintendo DSi and Nintendo Wii wireless connection test to complete, so that the Access point can be associated with. If this is not avaliable, Nintendo devices will be unable to join the wireless access point. 

Now ``BIND9`` is picky about permissions, but afterwards, can be started::
        
        chown named:named /etc/named.conf
        chown named:named /var/named/dynamic/*
        systemctl enable named.service
        systemctl start named.service

You can check that bind it working from the server, by running a query against localhost. In this case, we also try zone transfers (axfr)::

        dig @127.0.0.1 example.lan A
        dig @127.0.0.1 example.lan axfr
        dig @127.0.0.1 dhcp.example.lan axfr
        dig @127.0.0.1 1.0.4.10.in-addr.arpa PTR
        dig @127.0.0.1 0.4.10.in-addr.arpa axfr
        dig @127.0.0.1 conntest.nintendowifi.net A

From a client connected to the LAN side, you should NOT be able to carry out a zone transfer, but you should see the A and PTR records returned::

        dig @10.4.0.1 1.0.4.10.in-addr.arpa PTR
        dig @10.4.0.1 tollgate.example.lan. A
        dig @10.4.0.1 conntest.nintendowifi.net A
        dig @10.4.0.1 example.lan axfr

When a client connects you should see messages in ``/var/log/messages`` like::

        tollgate dhcpd: DHCPREQUEST for 10.4.0.10 from 00:00:00:00:00:00 (Franky) via p1p1
        tollgate dhcpd: DHCPACK on 10.4.0.10 to 00:00:00:00:00:00 (Franky) via p1p1
        tollgate dhcpd: Added new forward map from Franky.dhcp.example.lan. to 10.4.0.10
        tollgate dhcpd: Added reverse map from 10.0.4.10.in-addr.arpa. to Franky.dhcp.example.lan.

If you see messages like::

        tollgate dhcpd: Unable to add forward map from Franky.dhcp.example.lan. to 10.4.0.10: not found

Then you have made a mistake somewhere. Check that the rndc-key permissions are set to named:named, that dhcpd and named have been reloaded, that you have the correct control statements in named.conf and that in dhcpd.conf you have the primary option either as an ip or a resolvable hostname - We recommend this be the same as the IP in the named.conf control statement.

SQL
===

Django supports a number of SQL servers for it's operation. We have extensively tested MariaDB (Formerly MySQL) with Tollgate. However, PostgreSQL and SQLite are also valid options. 

MySQL / MariaDB
---------------

We have extensively tested Tollgate with MySQL and MariaDB. Additionally, they support replication features which allows for retrospective conversion to a clustered setup.

First install the mysql packages.::

        yum install MySQL-python mysql-server mysql

Now you need to setup the database. We advise you to remove the anonymous users and test tables, as well as setting a strong root password.::
        
        systemctl start mysqld.service
        mysql_secure_installation

Now we need to login to mysql, to create the database and tollgate user.::

        mysql -u root -p
        mysql> create database tollgate;
        mysql> create user 'tollgate'@'localhost' identified by 'password';
        mysql> grant all privileges on tollgate.* to 'tollgate'@'localhost';
        mysql> flush privileges;

Keep these details for when you configure the settings.py - You will need to remember the ``USER``, ``NAME`` and ``PASSWORD``. The ``HOST`` setting will be ``localhost``.

HTTPD
=====

Apache HTTPD is what provides the majority of ``Tollgate`` functionality. We highly recommend that you install ``mod_ssl``, ``mod_nss`` or ``mod_gnutls``, since tollgate requires user authentication's to be sent via the HTTP channels. Our examples below will cover the usage of ``mod_ssl``.

We must install ``mod_ssl``.::

        yum install mod_ssl

Next we create self signed certificates for use with ``Tollgate``.::

        cd /etc/pki/tls/private/
        openssl genrsa -out tollgate.key 2048
        openssl req -new -key tollgate.key -out tollgate.csr

It is ``CRUCIAL`` at this step, that when asked, you put in your servers hostname in the Common Name field.::

        Common Name (eg, your name or your server's hostname) []:tollgate.example.lan

Either you can send this CSR to be signed by another CA, or you can self sign. Either way, your resultant certificate should be tollgate.crt. Below is how you self sign your certificate::

        openssl x509 -req -in tollgate.csr -days 365 -signkey tollgate.key -out tollgate.crt

Now you should reconfigure the ServerName and ServerAlias parameters in ``/etc/httpd/conf.d/tollgate.conf``. Please note the VirtualHost for ``conntest.nintendo.net``. Do not modify this VirtualHost. 

Next you must edit ``/var/www/tollgate/tollgate_site/settings.py``. Fill in the ``DATABASE`` section with your SQL server information. Additionally, you should configure the ``SOURCE_URL`` parameter to ensure that you uphoad your AGPL obligations. Finally, at the bottom of the ``settings.py`` fill in your LAN details as needed. Check to make sure all values seem sane for your environment. 

NOTE: If you are using mysql, you must add to your settings.py ``USE_TZ = False``

Finally, we need to sync the database, and collect the static components ready for deployment.::

        cd /var/www/tollgate/tollgate_site
        python manage.py syncdb --noinput
        python manage.py migrate --noinput
        python manage.py collectstatic --noinput
        python manage.py createsuperuser

Now you should start httpd.::

        systemctl enable httpd.service
        systemctl start httpd.service    

Tollgate backends
=================

You should configure ``/etc/tollgate/backend.ini`` with your site details. Additionally, you should configure ``/etc/sysconfig/tollgate`` with the correct DNS name of your tollgate.

You can now start the tollgate backends.::

        systemctl enable tollgate-backend.service
        systemctl enable tollgate-captivity.service
        systemctl start tollgate-backend.service
        systemctl start tollgate-captivity.service



.. _rpmfusion-free: http://rpmfusion.org/Configuration
.. _tollgate repository: http://repo.tollgate.org.au/pub/fedora/

