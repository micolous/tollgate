# Captive Landing System #

When a request comes in for a site and you're not logged in to the captive portal, part of the captivity process is redirecting that request back to the captive portal page.  This also needs to be done in a way that has some funny HTTP headers (so that the client doesn't try to ever cache it) and that can handle requests from any site.

Both require a file called `tollgate_uri`.  You can generate it like this:

    # echo http://portal.example.tollgate.org.au/ > tollgate_uri

It's just a one-line configuration and both scripts will try to read from it.

There are two implementations of this handler here:

## CGI-based handler ##

TODO: Make this old handler available as an option in Backend.  At the moment the TPROXY handler is the only one that is available.

The CGI-based handler is in `index.py`.  This is the old setup.  You use mod_rewrite in Apache to listen on port 81, then REDIRECT all unknown HTTP traffic to the system.

## TPROXY-based handler ##

The TPROXY-based handler is in `tproxy.py`.  This is the new setup.  It uses the IP_TRANSPARENT options and listens for stuff sent by the TPROXY target in iptables.  It runs it's own web server that doesn't have to bind to an address, and acts like a transparent proxy server.  Only it answers all requests with a redirect.

Once the user is logged on and has quota, neither of these scripts handle web requests.

This requires Linux 2.6.28 or later.
