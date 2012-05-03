# Nintendo WiFi Connection web root #

On connecting to a network, a Nintendo gaming console (eg: DS, DSi, 3DS, Wii) will attempt to contact a server at http://conntest.nintendowifi.net/

If this fails at all, or results in a non-200 error code, the connection test will fail and the device will not connect to the network.  You won't even be given a prompt to login to a captive portal.

How to work around this is by running a local copy of the site, then using DNS spoofing to host the page locally.

It doesn't effect any other functionality of the Nintendo device.  Devices with a web browser (all bar the DS, which requires the Nintendo DS Browser game cartridge) can then log in to the captive portal directly on-device.

The page here should be **an exact replica** of the real connection test page, for compatibility reasons.  I've done some tests with hex-edited ROMs in the past, and pointed it at a different URL (to work around issues with other captive portals) and it has worked, however I have no idea if there's other games out there that rely on the content of this page.
