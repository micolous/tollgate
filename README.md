# tollgate README #

tollgate - A captive portal software for Linux for LAN parties.
Copyright 2008-2012 Michael Farrell <http://micolous.id.au>.

Version 3.1.0-dev "Tartar Control".

## Introduction ##

Welcome to tollgate.  This is a captive portal system for Linux, designed for operating LAN parties.  A lot of the concepts in the software are specific to how a LAN party operates, however you could use it for a sharehouse if you wanted, or something else.

It was originally called 'portal2'.  It managed the StreetGeek and SAGA internet connection for about two years, before I discontinued my involvement with the event.  It was called 'portal2' as it we previously experimented with a modified version of WiFiDog before abandoning it at the event.  It's changed the name to avoid potential trademark issues.

It consists of two parts, connected via dbus:

- A frontend system, which does most of the heavy lifting, including managing users and quota.  It is a Django website.
- A backend system.  This is only there to insulate the frontend from running programs as root directly.  It also abstracts calls to the firewall, and maintains the list of unmetered and blacklisted hosts.

This software isn't based on any existing captive portal solution - it's entirely from-scratch.  At the time that development started (2008) there wasn't any freely available software that did what we wanted, so I wrote one.

## Documentation ##

Full documentation for the project is located in the `docs` folder and may be generated with Sphinx.

Alternatively, it is available online at: http://tollgate.rtfd.org/

