# tollgate www #

This folder contains some static websites in order to make some software work with tollgate better.
 
## Nintendo WiFi Connection (WFC) ##

Provides compatibility for Nintendo gaming consoles (DS, Wii) with captive portals.  More information in it's `README.md` file.

## Web Proxy Auto-Discovery (WPAD) ##

`wpad` defines a proxy configuration of "direct".

The reason this is explicitly defined is because Windows machines will look up proxy server information from NETBIOS names after DNS, so if no `wpad` hostname is specified in DNS, the configuration may be pulled from a local machine with the name `wpad` with the `wpad.dat` file shared over HTTP.

An attacker could then use this to redirect all HTTP traffic for a system through their own proxy server, and hijack all requests.

This particularly effects Internet Explorer.

It's also good to set DHCP Option 252, and explicitly set a WPAD URL.

References:

 * [CVE-2009-0094](http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2009-0094), 2009-03-11
 * [MS09-008: Vulnerabilities in DNS and WINS Server Could Allow Spoofing (962238)](http://technet.microsoft.com/en-us/security/bulletin/ms09-008), 2009-04-12
 * [MSDN Blogs: We know IE: WPAD detection in Internet Explorer](http://blogs.msdn.com/b/askie/archive/2008/12/18/wpad-detection-in-internet-explorer.aspx), Aurthur Anderson, 2008-12-18
 * [Perimeter Grid: WPAD: Internet Explorer's Worst Feature](http://perimetergrid.com/wp/2008/01/11/wpad-internet-explorers-worst-feature/), Grant Bugher, 2008-01-11
 * [SkullSecurity: Pwning hotel guests](http://www.skullsecurity.org/blog/2009/pwning-hotel-guests), Ron Bowes, published 2009-11-19
