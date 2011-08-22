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


## Porting to non-Linux systems ##

I'd like to see this software ported to non-Linux systems.  I've done some preliminary research that's come up empty as yet as to operating systems with firewalls that meet all of the following requirements for tollgate's backend to work properly.

The majority of the work you'd need to do in porting the software is in the backend.  There's a little bit of Linux-specific frontend code to print out the contents of the ARP table.  All the backend is setup in a way that it calls from the frontend are abstracted away from iptables.

Before you start work porting it to a new operating system, please consider the following list of requirements.  If you can't get it to do **everything** in this list, then tollgate won't work.

* Ability to filter traffic by IP and MAC address.
* Port redirection, so captivity can work.  (ie: When you have no quota it redirects HTTP requests to a web server, resets all connections)
* Ability to filter based on quota remaining.
* Ability to do both positive and negative accounting.  Positive accounting is where you count upwards continuously the amount you've used, and negative accounting is where you decrement the amount you've used.  Many firewalls I've looked at only do positive accounting.
* Ability to have shared/named accounting labels.  So I can say "decrement counter X", and multiple rules can share that counter.
* Expose the counters via some `procfs` or `sysfs`-like interface.  For example, `xt_quota2` (the module we use in `iptables` for quota) exposes it's counters in `/proc/net/xt_quota/LABEL_NAME`.  With that you can read and write counters like files.
* Ability to access the ARP table.
* Doing all of the above stuff in kernel space.  Running an extra daemon isn't really an acceptable solution to me.


## Flow diagram (Linux) ##

This is how a packet is handled inside tollgate when running on Linux.

1. If it's a new connection, it hits the NAT table rules.
