.. _introduction:

************
Introduction
************

Welcome to tollgate.  This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

It consists of two parts, connected via dbus:

- A frontend system, which does most of the heavy lifting, including managing users and quota.  It is a Django website.
- A backend system.  This is only there to insulate the frontend from running programs as root directly.  It also abstracts calls to the firewall, and maintains the list of unmetered and blacklisted hosts.

It's important to note that tollgate only manages routing on your network.  A typical network will also need a DHCP server and DNS.  tollgate simply sets up NAT for you, and manages client access to the internet.

tollgate is a little bit different to most captive portal solutions because it doesn't use RADIUS at all.  It is entirely managed within your database, which can run on anything Django can such MySQL or SQLite.

Requirements
============

tollgate will only run on Linux.  You do not need to have your DHCP or DNS servers on the same machine (though is it recommended).

tollgate has some limited support for running the frontend, for development purposes, on Mac OS X and Windows.  However, the backend **will not work** on these systems.

At the time of writing, your author is not aware of any other operating system that supports the needed functionality to make the system work.  See :ref:`porting`.

The following packages must be installed:

- Python 2.5 or later
- Django 1.2 or later, as well as a supported database (such as MySQL or SQLite3).
- WSGI-compliant web server, such as apache2.
  - It is strongly recommended that you run the site using HTTPS only.
- Linux 2.6.28 or later with netfilter (most distributions ship with this).
- iptables 1.4.3 or later.
- xtables-addons 1.22 or later.
- DBUS
- django-south
- nmap
- python-daemon
- python-dbus
- python-iplib or python-ipy
- python-lxml
- python-simplejson (if using Python 2.5)


Optional dependencies:

- mrab-regex-hg


Client Platform Support
=======================

tollgate should allow any client with an IPv4 stack and a web browser to work with it.  The software has been tested with (but support is not limited to):

- Apple Mac OS X 10.4 and later
- FreeBSD
- Linux
- Microsoft Windows 98 and later
- Solaris

Because the software is designed for running LAN Parties, it also has support for gaming consoles, including those without web browsers, such as:

- Microsoft Xbox [#f1]_ [#f2]_
- Microsoft Xbox 360 [#f2]_
- Nintendo DS [#f3]_
- Nintendo DSi / 3DS
- Nintendo Gamecube [#f1]_ [#f4]_
- Nintendo Wii
- Sega Dreamcast [#f1]_ [#f3]_ [#f4]_
- Sony Playstation 2 [#f3]_ [#f4]_
- Sony Playstation 3

tollgate allows you to claim ownership of another device remotely, so if the device does not have a web browser, you can use this to login the device from something else.


.. rubric:: Footnotes

.. [#f1] This platform is untested, however should work.
.. [#f2] Platform lacks a web browser, so requires you to login from another device which does.
.. [#f3] Platform has a web browser application which isn't installed by default or requires purchase.  The web browser is not required, but will require you login with another device which has a web browser if you don't.
.. [#f4] Platform does not come with an in-built ethernet or wireless adapter as standard.
