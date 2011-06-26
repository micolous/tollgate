# Hacking on tollgate #

Tasks that I've got in mind at the moment:

## ipv6 support ##

I've started implementing IPv6 support in the backend of tollgate in a seperate branch.  At the moment it's got some basic backend support but I haven't implemented the frontend code just yet (or the scanning module for ipv6).  There's some stuff to consider though:

* `-t nat -j REDIRECT` doesn't work in ip6tables at all.  They have `-t mangle -j TPROXY` instead, which requires setting some "interesting" socket options (ie: I don't think Apache will work any more for the first stage of the captivity landing.
* IPv6 privacy extensions will mean you have a lot of constantly changing IPs.  We can handle this pretty easily though (at least for the outgoing connections) by having a browser window open that updates the IP address periodically (treating it similar to an IPv4 change).
* Incoming connections I want to have a flag on to say whether a host may be accessible from the outside world, defaulting to no.  As part of this getting the "permanent" IPv6 RA address may be important.  This can be done by a multicasted ping for most operating systems, or sniffing router advertisements.


## Improve the documentation ##

This is a fairly general task, anyone can pick this up.  Particularly a step-by-step installation guide would be helpful, or some sort of bootstrap script so you can put that on a system, it pulls deps and then the git repo.

As a secondary project, a virtual machine of this stuff would be good too, as well as some build script for making that VM from "nothing".  This could form part of a testing framework.


## Testing framework ##

There's no test cases, we probably should have some.


## Internationalisation / localisation ##

Started an `eo` (Esperanto) translation of the project a while ago, haven't really touched it since.  Many strings aren't in the translation files, and the setup of where the strings actually are could be improved a lot, because it's a mess.


