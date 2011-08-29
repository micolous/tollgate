# tollgate README #

tollgate - A captive portal software for Linux for LAN parties.
Copyright 2008-2011 Michael Farrell <http://micolous.id.au>.

## Introduction ##

Welcome to tollgate.  This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

It was originally called 'portal2'.  It managed the StreetGeek and SAGA internet connection for about two years, before I discontinued my involvement with the event.  It was called 'portal2' as it we previously experimented with a modified version of WiFiDog before abandoning it at the event.  It's changed the name to avoid potential trademark issues.

Currently this version is a little broken, as all StreetGeek and SAGA related components have been pulled out from under it.  There's also some policies for the event that were hard-coded into the software (such as one free quota reset).  I have however pulled out all copyrighted images from the source tree that may cause problems.

It's undergoing porting to LanConnect's data models, but that software is not yet released, so the system is in a state of flux.  At that point, a lot of those policies that were specific to the event will also be pulled out and replaced with something that's more flexible and easier to configure.

It consists of two parts, connected via dbus:

- A frontend system, which does most of the heavy lifting, including managing users and quota.  It is a Django website.
- A backend system.  This is only there to insulate the frontend from running programs as root directly.  It also abstracts calls to the firewall, and maintains the list of unmetered and blacklisted hosts.

This software isn't based on any existing captive portal solution - it's entirely from-scratch.  At the time that development started (2008) there wasn't any freely available software that did what we wanted, so I wrote one.

## Licensing ##

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.

A full copy of the license is available in the file /LICENSE.

Please be specifically aware of Section 13 "Remote Network Interaction; Use with the GNU General Public License."  This requires you to make modifications to this software available to network users.  The easiest way you can do this is by making a publicly available Git repository for your users.  (GitHub has a nice 'fork' option, which makes it easy for me to track this stuff...)

A notice will appear on all pages unless you set the SOURCE_URL setting to a location where the source code is stored.  This is enforced as some members of the LAN community in my experience are "lax" about following licensing obligations.  Removing the code that enforces this *does not* exempt you from the agreement - it is only there as a reminder and to assist you in license compliance.

Pushing your changes upstream is a great thing to do -- it not only assists other users of the software, but also assists you as internally-developed features don't have to be patched in every time there is a new release.

### flot ###

This software uses flot, a jQuery library for generating charts, copyright 2007-2009 IOLA and Ole Laursen.  A full copy of it's license is included in /media/flot/LICENSE.txt.  It's terms ONLY apply to the flot library - not to the rest of the tollgate source code.

flot itself also includes:

 - excanvas: Copyright 2006 Google Inc., licensed under the terms of the Apache License v2.0.
 - jQuery: Copyright 2009 John Resig and The Dojo Foundation, dual-licensed under the MIT and GPL.
 - in jquery.flot.navigate.js:
   - jQuery.event.drag: Copyright 2008 Three Dub Media <http://threedubmedia.com>, MIT licensed
   - jquery.mousewheel: Copyright 2009 Brandon Aaron <http://brandonaaron.net> dual-licensed under the MIT and GPL.

Additional licensing information about these components is in headers of their source files (in /frontend/media/flot/).

### Virtue font ###

The font 'virtue.ttf' is copyright 1997-1999 Marty P. Pfeiffer at Scooter Graphics.  It is released as freeware.

http://www.scootergraphics.com/virtue/index.html
http://www.dafont.com/virtue.font

## System Requirements ##

The recommended platform for this software is Debian GNU/Linux 6.0.  It has only been tested on i386, however should work correctly with other architectures as well.

There are the following requirements for successful operation:

- Python 2.4 or later.
- Django 1.2 or later, as well as a database module (such as sqlite3, python-mysql) and database server (if applicable).
- python-dbus, as well as a local DBUS installation
- A HTTPS-secured webserver to run the django site in (like apache2)
  - You could run the service without protection, but that's really silly.
- iptables 1.4.3 or later.
- Linux 2.6.14 or later, with netfilter support (most distributions ship with support for this).  However it has only been tested with 2.6 kernels.
- xtables-addons, you can either:
  - use v1.22 or later, as they include my patch.
  - It is available in GIT commit ID 7952a7d253a66a504df0589d4143088213451fe8 and later <http://xtables-addons.git.sourceforge.net/git/gitweb.cgi?p=xtables-addons/xtables-addons;a=commit;h=7952a7d253a66a504df0589d4143088213451fe8> which was added to the tree on Thu, 31 Dec 2009 15:24:47 +0000.
- python-iplib
- python-simplejson (if using Python <2.6)
- python-lxml
- django-south
- screen
- nmap

## Installation ##

I'm going to improve these instructions and provide a virtual appliance in the future, at the moment they're pretty bare.

To start, you should fork the tollgate repository in github (or fork it in a local git repository), then check out the sources.  You can then use this to select what changes to integrate from upstream, as well as managing your own contributions.  You should put tollgate into /opt/tollgate/.

You'll need to do these things:

* Install dependencies.
* Setup a database.
* Configure your network settings, DHCP and DNS.
* Configure the Django site in settings_local.py.  Remember to setup the SOURCE_URL to point to a website where your Git repository can be accessed.
* Setup a HTTPS site in Apache to point to tollgate's frontend Django application (mod_wsgi or mod_python).
* Setup a HTTP site in Apache to redirect to the HTTPS one.
* Setup a HTTP site on port 81 to run the CGI script captive_landing/index.py.  This is needed so browsers don't cache the redirects like they do with normal Apache redirects.
* Configure dbus for the tollgate backend service.
* Setup the tollgate backend service.
* Populate the database with OUIs and protocol numbers with the scraper.py script.  This will download the latest OUI and IPv4 protocol number definitions from IANA, and load them into tollgate's database.  This is needed for console detection and IPv4 port forwarding.
* Setup a cron job to run `./manage.py refresh_hosts` every 10 minutes or so.  This job will synchronise the in-kernel counters to a database, and look for new hosts on the network (and setup their internet access if they've been here before).

## Deployment Notes ##

### Clustering tollgate ###

tollgate can run in a clustered configuration with CARP (Common Address Redundancy Protocol).  You'll need to also set up redundant DHCP, DNS and database (eg: multi-master MySQL, or a single external database server) for this to work.

tollgate's quota saving procedures are written in such a way that it will work with multiple copies of tollgate simultaneously.  No special configuration of tollgate is required in order for it to work (apart from possibly changing database settings).

However, there is a window (between `refresh_hosts` calls, normally every 10 minutes) where you can use all of your quota via one tollgate and still have it available on the other, because the counters aren't synchronised live (and doing so is quite expensive).

In typical deployments however I haven't had this as a real problem, as it hasn't been possible to use more than 50% of the allocated quota in 10 minutes.  Doing so would require quite fast internet access, and you're generally competing for that resource with other clients on the network.

Be sure when configuring your network infrastructure for redundancy that:

* Your two tollgate machines have different power sources.  This could mean they're supplied via a different mains circuit, or one of them has a battery backup.
* You also provide redundancy for the switch, if you have one.
* You have either a multi-master database server setup, or a single database server with redundant power supplies or battery backup.
* If running with one database server, make sure that if one half of your power goes down, that the database server is still accessible (ie: use two switches and two NICs in your database server).
* Use protocols like Spanning Tree Protocol (STP) on your switches to break routing loops.

At the moment, tollgate doesn't support running multiple instances of itself managing *different* subnets.  That's a plan for down the track.

### Running on large subnets (>/24) or with more than 128 hosts ###

You may encounter performance issues or hosts dropping out "randomly" when running the software on subnets larger than a /24.  This is because of the size of the ARP table in Linux is effectively limited to 128 hosts, and the software will automatically send large amounts of ARP requests to see who currently holds each IP address on the network.

It is at this point you should seriously consider the size of your subnet.  If you have less than 200 hosts on your network, then you really only need a /24.  If you have a proper network plan in place, with DNS and static DHCP entries setup, you can still segment your network a lot more tightly.  You can use hostnames to provide memorable names to services, rather than wanting 10.0.13.37 when all your other hosts are in 10.0.1.0/24.

When you're planning for a LAN party, I generally do the math based on hosts = (maximum_attendance * 2) + static_hosts.  You should only be using a /16 if you're expecting 30,000+ people attending your LAN.  And even then you should consider slicing it up into subnets, because most operating systems have an ARP cache limit of about 1024 hosts.  With dynamic DNS assignments by DHCP and routing in place, you can even keep it so that hostnames across subnets can still talk to each other by name.  Without this, you'll end up with a lot of "noise" on your network from all sorts of multicast protocols.

You can tweak the behaviour of the ARP cache on Linux to let you have a bigger ARP table.  But this comes at a price -- it uses more memory, and the cron job for tollgate's refresh process will take much longer.

Linux provides three settings in /proc/sys/net/ipv4/neigh/default/:

* `gc_thresh1`: 128 hosts.  This is the minimum number of entries to keep in the ARP cache.  The garbage collector will not run if this amount isn't exceeded, and will reduce the number of entries every 30 seconds by default.
* `gc_thresh2`: 512 hosts (gc_thresh1 * 4).  This is the soft-maximum number of entries to keep in the ARP cache.  The garbage collector will allow this to be exceeded for 5 seconds.
* `gc_thresh3`: 1024 hosts (gc_thresh2 * 2).  This is the hard-maximum number of entries to keep in the ARP cache.  It will always run if there are more entries in the cache.

You should keep those ratios if you adjust it, but gc_thresh needs to be able to handle the base amount of hosts on your network.  So if you have 1024 hosts on your network, you'll need to tweak it so that:

* gc_thresh1: 1024 hosts
* gc_thresh2: 4096 hosts
* gc_thresh3: 8192 hosts

You can put these settings in /etc/sysctl.conf as net.ipv4.neigh.default.gc_thresh*, and it will apply on every boot.

## xtables-addons Installation Notes ##

xtables-addons requires at least iptables 1.4.3.  Debian GNU/Linux 5.0 "lenny" contains 1.4.2.  squeeze contains iptables 1.4.8.

### Automatic Installation with module-assistant ###

If you have xtables-addons-source 1.22-1 or later available to you, this will have the required patches available.  You can easily install the package with module-assistant:

    apt-get install module-assistant
    m-a a-i xtables-addons

### Manual Installation ###

You'll also need `build-essential`, `autoconf`, `automake`, `libtool`, `iptables-dev`, `linux-headers-2.6-686` and `pkg-config` to compile `xtables-addons`.  Make sure you run `./autogen.sh` again if you were missing packages when you last ran it, otherwise it may repeatedly fail when you re-run `./configure`.

So, installation process for that part:

    apt-get install build-essential autoconf automake libtool iptables-dev linux-headers-2.6-686 pkg-config
    ./autogen.sh
    ./configure
    make
    make install
    cp -s /usr/local/libexec/xtables/* /lib/xtables/

## Known Issues ##

- `xt_quota2` doesn't always show current quota data in iptables command.  It should not be relied on for accurate display of quota information via `iptables` command, use `/proc/net/xt_quota/` instead because that is accurate.  The actual accounting process is accurate however.
	- This may only effect SMP systems, but using procfs is still recommended.
	- Why the in-kernel quota system doesn't work for us: http://bugzilla.netfilter.org/show_bug.cgi?id=541
- Port forwarding doesn't work correctly when the internal and external ports are different.
- There's no way to deregister a console from an account that hasn't signed in to the current event.  (ie: Previous event the console is marked as being owned by user X, next event user Y can't sign it in because user X hasn't attended)
