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

Install tollgate, either using an official stable build, git repository, or distribution package.  You can install the latest `master` version of tollgate using `pip` with this command:

   $ sudo pip install git+https://github.com/micolous/tollgate.git

This **may** not work though, as the state of `git master` may be in flux.

This will install the entire `tollgate` package into your Python path, and install the captivity and backend daemons.

Configure DBUS
--------------

We need to add some configuration files for tollgate to DBUS' configuration in order to allow the web server process to use tollgate's backend.

In ``example/dbus/system.d/tollgate.conf`` are some example configuration you can use with tollgate.  Copy this to ``/etc/dbus-1/system.d/``, and modify with the appropriate username that the webserver uses (if it is not ``www-data``).

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
   'south', 
   'tollgate.api', 
   'tollgate.frontend',
   'tollgate.scripts'

You should also add the following extra settings for tollgate and configure appropriately::

   LAN_SUBNET='10.4.0.0/23'
   LAN_IFACE='eth1'
   DEFAULT_QUOTA_AMOUNT=150
   RESET_EXCUSE_REQUIRED=True
   RESET_PURCHASE=False
   ONLY_CONSOLE=False
   RESTRICTED_CALLS_KEY=''
   LOGIN_URL='/login/'
   LOGOUT_URL='/logout/'

The final setting to add is a URL where you are hosting the tollgate sources with your modifications.  You should **never** link back to the official tollgate repository using this method (there is already a link to the official repo on the source page).

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

An example configuration is given in ``examples/tollgate.cron``.  You will need to adapt it to point to the path of your Django project.

Configure webserver
-------------------

You'll need to now configure your web server.  You may wish to copy ``tollgate/tollgate.wsgi`` and use it in your own project folder.

There is an example apache2 configuration, including all vhosts, in ``example/apache2/tollgate-vhost``.

You will need to modify the path of static items (like the WPAD and WFC vhosts, and aliases for static files) to the appropriate locations, and URLs.

Included in the examples is how to configure a gitweb instance.  You could also push code changes to an external repository, however it must be accessible to users at all times (ie: you should mark it as "unmetered").

Start the daemons
-----------------

The first time you run you'll need to manually start the daemons.  They will start automatically on next boot.

Deployment Notes
================

Clustering tollgate with CARP
-----------------------------

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

Running on large subnets (>/24) or with more than 128 hosts
-----------------------------------------------------------

You may encounter performance issues or hosts dropping out "randomly" when running the software on subnets larger than a /24.  This is because of the size of the ARP table in Linux is effectively limited to 128 hosts, and the software will automatically send large amounts of ARP requests to see who currently holds each IP address on the network.

It is at this point you should seriously consider the size of your subnet.  If you have less than 200 hosts on your network, then you really only need a /24.  If you have a proper network plan in place, with DNS and static DHCP entries setup, you can still segment your network a lot more tightly.  You can use hostnames to provide memorable names to services, rather than wanting 10.0.13.37 when all your other hosts are in 10.0.1.0/24.

When you're planning for a LAN party, I generally do the math based on hosts = (maximum_attendance * 2) + static_hosts.  You should only be using a /16 if you're expecting 30,000+ people attending your LAN.  And even then you should consider slicing it up into subnets, because most operating systems have an ARP cache limit of about 1024 hosts.  With dynamic DNS assignments by DHCP and routing in place, you can even keep it so that hostnames across subnets can still talk to each other by name.  Without this, you'll end up with a lot of "noise" on your network from all sorts of multicast protocols.

You can tweak the behaviour of the ARP cache on Linux to let you have a bigger ARP table.  But this comes at a price -- it uses more memory, and the cron job for tollgate's refresh process will take much longer.

Linux provides three settings in ``/proc/sys/net/ipv4/neigh/default/``:

* ``gc_thresh1``: 128 hosts.  This is the minimum number of entries to keep in the ARP cache.  The garbage collector will not run if this amount isn't exceeded, and will reduce the number of entries every 30 seconds by default.
* ``gc_thresh2``: 512 hosts (gc_thresh1 * 4).  This is the soft-maximum number of entries to keep in the ARP cache.  The garbage collector will allow this to be exceeded for 5 seconds.
* ``gc_thresh3``: 1024 hosts (gc_thresh2 * 2).  This is the hard-maximum number of entries to keep in the ARP cache.  It will always run if there are more entries in the cache.

You should keep those ratios if you adjust it, but gc_thresh needs to be able to handle the base amount of hosts on your network.

``tollgate-backend`` will automatically set this for you if you set the ``arp_table_size`` option in ``backend.ini``::

   arp_table_size = 512


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
