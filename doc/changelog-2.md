# portal2 (tollgate) changelog (2.x) #

## Changes in 2.8.3 (September 2010) ##

 * Updated internal documentation.
 * Removed documentation that isn't used anymore in favour of the wiki.
 * Server-side graph generation replaced with client-side (javascript) one for peformance reasons.
 * "My devices and quota" now only updates the information from the kernel space if it hasn't happened in the last 2 minutes.
 * API allows cookie-based authentication for faster authentication and better browser integration.
 * Clustering support.
 * UserProfile objects returned by the API now return the user's Forum UID, so username changes can be handled by API callers, and better integrate with the website.
 * API now implements new `python` output method, which is the output from the [`repr()`](http://docs.python.org/library/functions.html#repr) function.


## Changes in 2.8.2 (July 2010) ##

 * A user's first and last name is no longer returned by any API call except for `whoami()`.  Other methods which request a `UserProfile` object will have empty strings instead of the user's name.


## Changes in 2.8.1 (May 2010) ##

 * Clarified the "no api" login error message reasons, because there are more reasons why it can occur than were listed.
 * Added a test version of the 'modern' and 'platinum' themes.  These are incomplete.
 * Out-of-subnet error page was not added to version control, now it is.
 * `libiptc-python` removed, as it is no longer required.
 * Fixed captivity bug where a user with unlimited quota would be forever stuck captive.


## Changes in 2.8.0 (January 2010) ##

 * Fixed an exploit that would allow an attacked user to gain unlimited internet quota through an issue with external authentication.
 * Fixed an issue where calls to the Django-side API would not convert the user_id to a string.  This is now done in the API, so these calls will now (implicitly) succeed.  This fixes an issue where quota wasn't automatically being recorded as part of the crontab job.
 * Quota data is now automatically recorded every 10 minutes with history.
 * There is a bandwidth graph showing a 10-minute average of metered internet usage over time.
 * 'cake' and 'terminal' themes now have text boxes fully enclosed, rather than just an underline.
 * Removed some duplicate code relating to quota reporting to backend.
 * Reworked backend to use `xt_quota2` instead of the normal iptables quota module.
 * tollgate is now finally captive!  YAY!
 * Fixed an error in the "internet login success" page where it would either not display at all or still show the survey banner on some browsers.
 * Fixed an issue where external IP addresses could be logged into tollgate.
 * Fixed an issue where IP changes might not be taken into account because expired entries in the ARP cache were not ignored.
 * Admin: Internet usage report now defaults to being sorted by username alphabetically instead of by user ID.
 * Admin: Internet usage report includes current speed of user's traffic.
 * i18n: Started adding internationalisation hooks.
 * API: Added HTTP GET API with json, pickle and csv output modes.
 * Removed support for `libiptc-python` in backend.


## Changes in 2.6.6 (November 2009) ##

 * LANdit backend also grabs whether a user has ordered unlimited coffee.
 * `coffee_ip` API call added.
 * Added option to manually change whether a user is allowed to use the coffee notification system, and extra ACL added to determine whether an administrator is allowed to change that value.
 * Internet connectivity is no longer switched on on login **if** you have previously disabled internet connectivity and haven't selected to sign the current computer on in your name.
 * Backend not running will no longer cause EventAttendance migration failure on login.
 * Clarified the meaning of "structure" in the API help to mean a dict(ionary).
 * `*_mac` versions of the API calls were removed.


## Changes in 2.6.5 (October 2009) ##

 * ACL fixes.
 * New version of the reset lecture.
 * Warning added that the "logout" button logs you out of the web interface, not internet access.
 * You can now "disown" a host.
 * Host scanning changed from `nbtscan` to `nmap`.
 * Hosts names are now grabbed from DNS rather than NetBIOS.


## Changes in 2.6.4 (September 2009) ##

 * You can now only reset your quota once you have used 70% of it.
 * Reset lecture added.
 * Reset logging implemented.
 * Network host changes now logged.
 * You can now choose different themes, including using the old (green) 'terminal' theme.  The default theme is the same as from 2.6.2, the 'cake' theme.
 * The 'cake' theme now has underlines on submit buttons.
 * `libiptc-python` created (a libiptc module for python)
 * Backend ported to allow the use of libiptc-python.  Currently disabled due to bugs.
 * The automated host scan now also synchronises kernel-level counters with the database at that time.


## Changes in 2.6.3 (July 2009) ##

 * Internal organisational changes to program structure.
 * Backend API framework changed from XMLRPC to DBUS.


## Changes in 2.6.2 (June 2009) ##

 * New backend authentication API for LANbru.
 * Improved administration interface.
 * New theme.
 * Better error handling system.


## Changes in 2.6.1 (May 2009) ##

 * Fixed whoami() API call so that it works.
 * Added usage() API call.
 * Fixed an issue where ownership would not be reassigned locally where
	it should have been allowed to be.


## Changes in 2.6.0 (April 2009) ##

 * Resynced the two versions of v2.5 of the code in use.
 * When there is an external authentication failure (such as attendance not registered, or forum password change) on an already-migrated account, you are no longer kept logged in.
 * Offline hosts are now marked as being offline properly.
 * Added API for interacting with tollgate.
 * Version numbering changed


## Changes in 2.5 (March 2009) ##

 * Fixed an issue where an automated task to find active hosts was failing and not marking offline ones as offline.


## Changes in 2.4 (February 2009) ##

 * Added additional administrative controls.
 * Added standalone portal mode.
 * Menu links are now much clearer.
 * Security: Improved handling of offline hosts that could allow a user to gain additional quota.


## Changes in 2.3 (January 2009) ##

 * Lots more error handling code


## Ancient Changes ##

First versions 2.0 - 2.2 were from October - December 2008.  These were often pulled shortly after the start of the LAN due to bugs.  It was later found that many of these problems were related to faulty networking equipment.  The equipment has since been replaced.

The system was implemented due to issues with the previous WiFiDog-based setup (GLaDOS).

 * Quota limits are now done kernel level so it is much more accurate and cut-offs are instant (previously a 10 minute window).
 * Can now log in to more than two consoles at once.
 * Logout timeouts removed.
