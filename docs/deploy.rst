******************
Deploying tollgate
******************

Deploying tollgate into a Django project
========================================

The "proper" way to deploy tollgate is to install the software (using ``setup.py``), and then create a Django project with tollgate setup inside of it.

This is achieveable fairly simply, however be aware that **tollgate only manages routing**, it does **not** manage things like DNS and DHCP which you'll need to make your network actually accept clients.

This has the advantage of allowing you to easily customise configuration and templates.  Be aware though that all modifications to tollgate **must** be made available, as well as the software itself, to all of your users, as a condition of the license.

Pre-requisites
--------------

I'm assuming here that you have:

* Installed and configured an apache2 server with mod_wsgi and mod_ssl.
* Installed and configured a database server, for example, MySQL, as well as installed appropriate Python bindings to allow interaction.
* Installed everything else you need to make your network work -- that is, DHCP server, DNS server, multiple network interfaces in your tollgate machine (which will be your router / default gateway).
* Installed and configured DBUS.
* Installed other dependencies.
 
Installation and configuration of those is outside of the scope of this document.  If you're looking up HOWTO documents on the internet, do not do anything with `iptables`, as setting up a NAT and routing itself is part of tollgate.

Install tollgate
----------------

Install tollgate, either using an official stable build, git repository, or distribution package.  You can install the latest `master` version of tollgate using `pip` with this command::

   $ sudo pip install git+https://github.com/micolous/tollgate.git

This **may** not work though, as the state of `git master` may be in flux.

This will install the entire `tollgate` package into your Python path, and install the captivity and backend daemons.

Configure DBUS
--------------

We need to add some configuration files for tollgate to DBUS' configuration in order to allow the web server process to use tollgate's backend.

In ``docs/example/dbus/system.d/tollgate.conf`` are some example configuration you can use with tollgate.  Copy this to ``/etc/dbus-1/system.d/``, and modify with the appropriate username that the webserver uses (if it is not ``www-data``).

Then reload the DBUS configuration with ``/etc/init.d/dbus reload``.

Create a project
----------------

Now, you should create a Django project for tollgate to use.  This won't have any of tollgate's code in this folder -- it will reference a the system-installed copy. ::

   $ django-admin startproject mylanportal

This will create some boilerplate code for a Django site.  Currently, tollgate doesn't support not being at the root of the site, but this may change in the future.

From here on in, I'm going to assume your project name is `mylanportal`.

Configure the project
---------------------

Jump into the ``mylanportal/mylanportal/urls.py``.  Change it so it includes ``tollgate.urls``.  ``tollgate.urls`` will also give you the Django admin site, and the internationalisation configuration app.  It should look something like this::

   from django.conf.urls.defaults import patterns, include, url
   urlpatterns = patterns('',
	 (r'^', include('tollgate.urls')),
   )

The next step is to setup ``settings.py``.

Near the top, add these lines::

   from os.path import *
   PROJECT_PATH = realpath(dirname(__file__))

This is a handy trick because you can use it to setup other paths later.

Setup the location of the database.  It is recommended you use MariaDB (MySQL).

You should also setup a ``STATIC_ROOT`` for where all the static files should be served from, and a ``STATIC_URL``.  Be aware that if you are deploying on a HTTPS site (which you should!) you need to make your resources also be on a HTTPS site.  The purpose of this is that outside of DEBUG mode, you're expected to serve static files external to Django -- as it is much faster.

To your ``INSTALLED_APPS``, append::

   'django.contrib.humanize',
   'django.contrib.admin',
   'djangorestframework',
   'south', 
   'tollgate.api', 
   'tollgate.frontend',
   'tollgate.scripts'

You should also add the following extra settings for tollgate and configure appropriately::

   AUTH_PROFILE_MODULE = 'frontend.userprofile'
   LAN_SUBNET='10.4.0.0/23'
   LAN_IFACE='eth1'
   DEFAULT_QUOTA_AMOUNT=150
   RESET_EXCUSE_REQUIRED=True
   RESET_PURCHASE=False
   ONLY_CONSOLE=False
   RESTRICTED_CALLS_KEY=''
   LOGIN_URL='/login/'
   LOGOUT_URL='/logout/'

The final setting to add is a URL where you are hosting the tollgate sources with your modifications, ``SOURCE_URL``.  You should **never** link back to the official tollgate repository using this method (there is already a link to the official repo on the source page).

Not hosting the source code yourself may expose you to legal liability.

Configure daemons
-----------------

Install the init scripts and backend configuration::

   $ sudo cp platform/debian/init.d/* /etc/init.d/
   $ sudo cp platform/debian/default/* /etc/default/
   $ sudo mkdir /etc/tollgate/
   $ sudo cp example/tollgate/backend.ini /etc/tollgate/

Modify the scripts (``tollgate-backend`` and ``tollgate-captivity``) as appropriate to match the path to the tollgate_backend and tollgate_captivity scripts.

Edit ``/etc/default/tollgate-captivity`` to point to the URL where tollgate is hosted.

To make the daemons start, run::

   $ sudo update-rc.d tollgate-backend defaults
   $ sudo update-rc.d tollgate-captivity defaults

Modify the backend configuration as appropriate for your network (``/etc/tollgate/backend.ini``).
	
We won't start the daemons just yet, though.

Configure cron
--------------

tollgate requires a periodic cronjob to refresh the list of hosts in it's database.

An example configuration is given in ``docs/example/tollgate.cron``.  You will need to adapt it to point to the path of your Django project.

Configure webserver
-------------------

You'll need to now configure your web server.

If you are using Django 1.3 or earlier, you may wish to copy ``tollgate/tollgate.wsgi`` and use it in your own project folder.  However, be sure to change the ``DJANGO_SETTINGS_MODULE`` to the name of your project (eg: ``mylanportal.settings``), as tollgate itself includes a ``tollgate.settings`` for use in development deployment.

In Django 1.4 or later, it will create a file named like ``mylanportal/wsgi.py`` with settings that you should use instead.

There is an example apache2 configuration, including all vhosts, in ``docs/example/apache2/tollgate-vhost``.

You will need to modify the path of static items (like the WPAD and WFC vhosts, and aliases for static files) to the appropriate locations, and URLs.

Included in the examples is how to configure a gitweb instance.  You could also push code changes to an external repository, however it must be accessible to users at all times (ie: you should mark it as "unmetered").

Start the daemons
-----------------

The first time you run you'll need to manually start the daemons.  They will start automatically on next boot.


Deploying tollgate in development
=================================

In development, you can run and deploy ``tollgate`` from within a git clone of the repository.  This is the "old" way of deploying tollgate in production, and has since been superceeded.

You can run tollgate in development either out of a WSGI-compatible webserver, or using Django's single-threaded development server.

Useful Functions
----------------

repair_permissions
^^^^^^^^^^^^^^^^^^

::

   $ python manage.py repair_permissions

Repairs execute permissions on scripts.

setup_settings
^^^^^^^^^^^^^^

::

   $ python manage.py setup_settings

Creates a ``tollgate/settings/local.py`` for your local settings, and configures your ``SECRET_KEY``.

Clustering tollgate with CARP
=============================

tollgate can run in a clustered configuration with CARP (Common Address Redundancy Protocol).  You'll need to also set up redundant DHCP, DNS and database (eg: multi-master MySQL, or a single external database server) for this to work.

tollgate's quota saving procedures are written in such a way that it will work with multiple copies of tollgate simultaneously.  No special configuration of tollgate is required in order for it to work (apart from possibly changing database settings).

However, there is a window (between ``refresh_hosts`` calls, normally every 10 minutes) where you can use all of your quota via one tollgate and still have it available on the other, because the counters aren't synchronised live (and doing so is quite expensive).

In typical deployments however I haven't had this as a real problem, as it hasn't been possible to use more than 50% of the allocated quota in 10 minutes.  Doing so would require quite fast internet access, and you're generally competing for that resource with other clients on the network.

Be sure when configuring your network infrastructure for redundancy that:

* Your two tollgate machines have different power sources.  This could mean they're supplied via a different mains circuit, or one of them has a battery backup.
* You also provide redundancy for the switch, if you have one.
* You have either a multi-master database server setup, or a single database server with redundant power supplies or battery backup.
* If running with one database server, make sure that if one half of your power goes down, that the database server is still accessible (ie: use two switches and two NICs in your database server).
* Use protocols like Spanning Tree Protocol (STP) on your switches to break routing loops.

At the moment, tollgate doesn't support running multiple instances of itself managing *different* subnets.  That's a plan for down the track.

Running on large subnets (bigger than /24) or with more than 128 hosts
======================================================================

You may encounter performance issues and hosts dropping out "randomly" when running the software on subnets larger than a /24.  This is because of the size of the ARP table in Linux is effectively limited to 128 hosts, and the software will automatically send large amounts of ARP requests to see who currently holds each IP address on the network.

Reality Check!
--------------

It is at this point you should seriously consider the size of your subnet.  If you have less than 200 hosts on your network, then you really only need a /24.  If you have a proper network plan in place, with DNS and static DHCP entries setup, you can still segment your network a lot more tightly.  You can use hostnames to provide memorable names to services, rather than wanting ``10.0.13.37`` when all your other hosts are in ``10.0.1.0/24``.

When you're planning for a LAN party, I generally do the math based on::

   hosts = (maximum_attendance * 2) + static_hosts

You should only be using a ``/16`` if you're expecting in excess of 30,000 people attending your LAN.  And even then you should consider slicing it up into subnets, because most operating systems have an ARP cache limit of about 1024 hosts, and you'll have problems with broadcast packets.  Even something as simple as a `Master Browser Election`_ could knock out your network (though you should be :ref:`usingwins` at this point).

With dynamic DNS assignments by DHCP and routing in place, you can even keep it so that hostnames across subnets can still talk to each other by name.  Without this, you'll end up with a lot of "noise" on your network from all sorts of multicast protocols.

At this point of time though, you'll need to setup multiple copies of tollgate: one to service each network.  However, each instance should be able to share a single database provided the IP addresses are unique.

There are, of course, some applications and games which simply won't work because they require multicast or link-local packets.  But it is also those games which become increasingly unreliable on large networks.

.. _Master Browser Election: http://support.microsoft.com/kb/188001

Tweaking Linux's ARP table
--------------------------

You can tweak the behaviour of the ARP cache on Linux to let you have a bigger ARP table.  But this comes at a price -- it uses more memory, and the cron job for tollgate's refresh process will take much longer.

Linux provides three settings in ``/proc/sys/net/ipv4/neigh/default/``:

* ``gc_thresh1``: 128 hosts.  This is the minimum number of entries to keep in the ARP cache.  The garbage collector will not run if this amount isn't exceeded, and will reduce the number of entries every 30 seconds by default.
* ``gc_thresh2``: 512 hosts (gc_thresh1 * 4).  This is the soft-maximum number of entries to keep in the ARP cache.  The garbage collector will allow this to be exceeded for 5 seconds.
* ``gc_thresh3``: 1024 hosts (gc_thresh2 * 2).  This is the hard-maximum number of entries to keep in the ARP cache.  It will always run if there are more entries in the cache.

You should keep those ratios if you adjust it, but gc_thresh needs to be able to handle the base amount of hosts on your network.

``tollgate-backend`` will automatically set this for you if you set the ``arp_table_size`` option in ``backend.ini``.

This will automatically set all three garbage collector thresholds appropriately according to the ratios above.

You absolutely require this value to be set to the number of hosts in your subnet, with a little bit of leeway for your WAN ethernet interface.  Which means if you have a ``/23`` (512 IPs) on your LAN side, and about 10 machines on your WAN side, you should set the value to about 530 (enough for both sides with some leeway)::

   arp_table_size = 530

If you set it to exactly 512, then the non-result ARP table entries will push out legitimate ones, and also entries from your WAN side will push out entries from your LAN size.

MySQL / MariaDB quirks
======================

There is an issue where Django will not create a big enough field type for ``PositiveIntegerFields``, resulting in data collection failing when there has been more than 4GB used, or if more than 4GB is allocated to a user.

You can patch the tables with this command on your deployed project::

	python manage.py mysql_bigint_patch

Windows Clients
===============

While this isn't a core issue inside of tollgate, there's a pretty strong chance when running LAN Party events that you will have a large amount of Microsoft Windows hosts.

There are many things that Windows doesn't handle properly, which will require some manual tweaking to sort out.  Most of these problems you will be blamed "for breaking it", despite there being problems in the Windows OS.

.. NOTE::
   These issues are not caused by tollgate.  They are simply included in this guide because they are problems not often documented in a single place.

Here are some problems your author has encountered in the past:

Multiple search domains do not work
-----------------------------------

In DHCP options, you can offer multiple DNS search domains.  On Windows, only the first search domain will be used.

You should separate your static (official) hosts and dynamic (user) hosts into two subnets still::

   css01.example.lan
   openttd1.example.lan
   irc.example.lan
   jimmy-pc.dhcp.example.lan
   janes-macbook-pro.dhcp.example.lan

You should then specify the resolution order as follows::

   example.lan      (Windows will only use this one)
   dhcp.example.lan

You can work around this bug, however it is an "opt-in" and requires some manual configuration in Windows:

#. Open Network and Sharing Centre.
#. Select the adapter to modify that is connected to the local network.
#. Click ``Properties``.
#. Click ``Internet Protocol Version 4 (TCP/IPv4)``.
#. Click ``Properties``.
#. Click ``Advanced``.
#. Click the ``DNS`` tab.
#. Select ``Append these DNS suffixes (in order):``.
#. Add entries for each DNS suffix your network uses.
#. Click ``OK``.
#. Click ``OK``.
#. Click ``Close``.
#. Click ``Close``.

Then this brings us to the next bug in Windows' DNS resolver:

Dotted-domain lookups are never recursive
-----------------------------------------

On a non-Windows machine, say you have a search domain set to ``example.lan``.  If you lookup ``jimmy-pc.dhcp``, it will look up ``jimmy-pc.dhcp.example.lan.`` then ``jimmy-pc.dhcp.``.

On a Windows machine, it assumes any name being resolved with a dot in it is actually being resolved as a root object (ie: ``jimmy-pc.dhcp`` internally becomes ``jimmy-pc.dhcp.``), so it will never try to look up ``jimmy-pc.dhcp.example.lan.``

We can work around this with a DNAME zone for ``dhcp`` similar to this::

   dhcp. IN SOA ns1.example.com. root.example.com (
         2010012301 ; serial
         60         ; refresh (1 minute)
         60         ; retry (1 minute)
         3600       ; expire (1 hour)
         60         ; minimum (1 minute)
         )
         NS      tollgate.example.lan.
   
   dhcp. IN DNAME dhcp.example.lan.

   
Web Proxy Auto-Discovery Vulnerabilities
----------------------------------------

Internet Explorer on Windows will try to discover a proxy server by doing NetBIOS lookups for the server called ``WPAD`` by default.  As a result, a local network user may intercept all traffic from a vulnerable computer by specifying proxy settings that redirect traffic.

Included in tollgate's source repository is a site at ``/www/wpad/``.  This should be hosted at the server named ``wpad.example.lan.`` and ``wpad.`` (where ``example.lan.`` is your search domain).

Likewise, you should send DHCP option 252 to indicate an absolute path to the WPAD configuration.  In ISC DHCPd, you can do this with::

   option auto-proxy-config code 252 = string;
   subnet 10.4.0.0 netmask 255.255.255.0 {
     # ... some other configuration here
   
     option auto-proxy-config "http://10.4.0.1/wpad.dat";
   }

See also:

* `CVE-2009-0094`_, 2009-03-11
* `MS09-008`_: Vulnerabilities in DNS and WINS Server Could Allow Spoofing (962238), 2009-04-12
* MSDN Blogs: We know IE: `WPAD detection in Internet Explorer`_, Aurthur Anderson, 2008-12-18
* Perimeter Grid: WPAD: `Internet Explorer's Worst Feature`_, Grant Bugher, 2008-01-11
* SkullSecurity: `Pwning hotel guests`_, Ron Bowes, published 2009-11-19

.. _CVE-2009-0094: http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2009-0094
.. _MS09-008: http://technet.microsoft.com/en-us/security/bulletin/ms09-008
.. _WPAD detection in Internet Explorer: http://blogs.msdn.com/b/askie/archive/2008/12/18/wpad-detection-in-internet-explorer.aspx
.. _Internet Explorer's Worst Feature: http://perimetergrid.com/wp/2008/01/11/wpad-internet-explorers-worst-feature/
.. _Pwning hotel guests: http://www.skullsecurity.org/blog/2009/pwning-hotel-guests

.. _usingwins:

Using WINS
----------

In an effort to help reduce the master browser election traffic, and assist in NetBIOS name resolution, you should setup a WINS server.

In ISC DHCPd, this is done with the following configuration option::

   option netbios-name-servers 10.4.0.1;

You'll also need to run an actual WINS server too.  Samba 3 provides a WINS server, but it is not enabled by default.  In the ``[global]`` section of ``/etc/samba/smb.conf``, you can enable this functionality with::

   wins support = yes
   dns proxy = yes

After this, reload your Samba and DHCP daemon.

Mass-mailing Worms
------------------

It's pretty much a given you will have problems with infected Windows hosts.  One major thing you will want to consider is blocking external SMTP traffic to at least prevent your network from becoming a spam hub, and angering your ISP (as well as other internet users).  You can do this with an entry in ``backend.ini``, under the section ``blacklist``::

   externaldns = 0.0.0.0/25
   
Normally you only have to block port 25 traffic.  SMTP over SSL is generally never used by such worms, and mail servers running on SSL generally also require authentication (which the spam bots won't have).

It will also allow legitimate senders of mail on your network to be able to continue sending mail.

Unfortunately, there isn't a simple way at this time to exempt blocking of SMTP over TLS (which uses port 25 and ``STARTTLS`` command).  Additionally, many ISPs do not offer encrypted SMTP servers -- until they are lobbied by users. ;)


Nintendo Consoles / WFC
=======================

.. WARNING::
   Nintendo DS and DS Lite, as well as any DS games on the DSi and 3DS will **only** connect to wireless networks that are either unencrypted or encrypted with WEP.  Additionally, they will only connect to 2.4GHz 802.11b networks.
   
   Because of the additional radio bandwidth that 802.11b clients require, it is recommended that you run a seperate 802.11b-only network for those devices.
   
.. NOTE::
   On the Nintendo DSi and 3DS, connection profiles 1 - 3 do not support WPA or WPA2 encryption (for compatibility with DS games), only the profiles 4 - 6 support it.

All of Nintendo's gaming consoles, with the exception of the Gamecube, will probe a site called ``conntest.nintendowifi.net`` during connection setup.

If this site is inaccessible or does not return a "200 OK" response, the console will assume it cannot connect to the internet, and refuse to save the connection profile.

Included in tollgate's source repository in ``/www/wpad/`` is a website you can host at ``conntest.nintendowifi.net``, with a DNS record pointing to your server.  This must be accessible inside of your LAN.

Playstation Portable (PSP)
==========================

.. WARNING::
   Playstation Portable will only connect to 2.4GHz 802.11b networks, and does not support WPA2 encryption.
   
   Because of the additional radio bandwidth that 802.11b clients require, it is recommended that you run a seperate 802.11b-only network for those devices.

.. WARNING::
   Playstation Portable E-1000 does not have WiFi.

PSP System software v2.00 includes a web browser.  Earlier versions of the system software do not include a web browser.

If you wish to sign earlier versions of the PSP into tollgate, you will need to do it from another device with a web browser.

Consoles without web browsers
=============================

The general process for logging a system into tollgate when the device does not have a web browser is:

#. Set the hostname of the device to be something uniquely and easily identifiable.
#. Connect the device to the network.
#. Attempt a connection test (this will fail).
#. Find the device in tollgate's `login other computers` screen, and sign it in.
#. Reattempt the connection test (this should succeed).

After this, the device will be registered with that user's account.  Whenever they are signed into the event they will automatically grant access to the internet for all of their devices.

Rogue DHCP / DNS Servers
========================

There have been several instances at events your author has administed where Windows worms propegating on the network will send out rogue DHCP server responses, attempting to either route traffic through the infected machine, or replace DNS with a third-party server that will redirect traffic to popular websites through an attacker's server.

There are two major mitigation steps you should take:

Block external DNS servers
--------------------------

This can be done in ``backend.ini``, by adding a blacklist line like::

   externaldns = 0.0.0.0/53

This will only allow your DNS server, and any whitelisted / unmetered servers to have DNS traffic passed through to them.

Use layer 3 managed switches with DHCP filtering
------------------------------------------------

Layer 3 managed switches offer various filtering options.  You can limit the spread of a rogue DHCP server by:

1. Only allowing DHCP to be served from the tollgate server(s) port(s) on the backbone switch.
2. Only allowing DHCP to be served from the port(s) connecting to the backbone switch for leaf switches.

If you are low on budget, there's a good chance that you will not be able to afford all Layer 3 managed switches.  In this case, save the money for at least one on your backbone, so any rogue DHCP server issues will be limited to one leaf switch, and you'll be able to quickly determine which host is compromised.

