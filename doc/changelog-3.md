# tollgate changelog (3.x series) #

This document describes releases in the 3.x series of tollgate.  All releases in the 3.x series are named after types of toothpaste.

## 3.0.0 "Cavity Protection" (May 2012) ##

** NOTE: IS UNRELEASED AT PRESENT, UPDATE WHEN STABLE VERSION **

This represents the first public stable release of tollgate (formerly portal2).  Changes from 2.8.3 (September 2010):

 * Added basic IPv4 port/protocol forwarding ability.
 * Application migrated to `setuptools`-based deployment, and can be hosted inside of another Django project in typical deployment.
 * Improved documentation.
 * License changed to Affero GPL v3.
 * Major repository shuffle and cleanups.

 * `api`: NetworkHost objects now report a bit more information about the vendor (not just the type of console), match many non-console items.  Consoles are now identified by a new `is_console` field.

 * `backend`: Tollgate `backend` daemonised, renamed files.  Created init scripts.
 * `backend`: Configuration file absence now handled better. (Issue #10)
 * `backend`: Default configuration location is now `/etc/tollgate/backend.ini`.
 * `backend`: New `TPROXY`-based captivity handler backported from experimental IPv6 branch.

 * `builder`: Added new `tollgatebuilder` script for experimental deployment documentation. ;)

 * `frontend`: Absence of `python-dbus` is handled more gracefully, allowing testing and development of the frontend on non-DBUS systems (Windows).
 * `frontend`: Added system for automatically downloading and parsing MAC OUIs for system identification.
 * `frontend`: All StreetGeek and SAGA-specific authentication code has been removed, as well as all external authentication code.
 * `frontend`: All sign-ins and events are now handled locally, and locally administerable with sign-in wizard.
 * `frontend`: Platform-specific code has been abstracted out, and moved into seperate modules, with a dummy fallback module for non-supported platforms (non-Linux).
 * `frontend`: Remove several redundant (non-minimised) and unused Javascripts.
 * `frontend`: Use django.contrib.staticfiles. (Issue #8)
 * `frontend`: When `iplib` is not available, also attempt to use `IPy`. (David B @d1b)
 * `frontend`: **Security**: Fixed issue where arbitrary protocols would be included on the captive landing page, leading to XSS issue. (Reported by David B @d1b)

