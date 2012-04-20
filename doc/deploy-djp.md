# Deploying tollgate into a Django project #

The "proper" way to deploy tollgate is to install the software (using `setup.py`), and then create a Django project with tollgate setup inside of it.

This is achieveable fairly simply, however be aware that **tollgate only manages routing**, it does **not** manage things like DNS and DHCP which you'll need to make your network actually accept clients.

This has the advantage of allowing you to easily customise configuration and templates.  Be aware though that all modifications to tollgate **must** be made available, as well as the software itself, to all of your users, as a condition of the license.

## Pre-requisites ##

I'm assuming here that you have:

 * Installed and configured an apache2 server with mod_wsgi and mod_ssl.
 * Installed and configured a database server, for example, MySQL, as well as installed appropriate Python bindings to allow interaction.
 * Installed everything else you need to make your network work -- that is, DHCP server, DNS server, multiple network interfaces in your tollgate machine (which will be your router / default gateway).
 * Installed and configured DBUS.
 * Installed other dependencies.
 
Installation and configuration of those is outside of the scope of this document.  If you're looking up HOWTO documents on the internet, do not do anything with `iptables`, as setting up a NAT and routing itself is part of tollgate.

## Install `tollgate` ##

Install tollgate, either using an official stable build, git repository, or distribution package.  You can install the latest `master` version of tollgate using `pip` with this command:

    $ sudo pip install git+https://github.com/micolous/tollgate.git

This **may** not work though, as the state of `git master` may be in flux.

This will install the entire `tollgate` package into your Python path, and install the captivity and backend daemons.

## Configure DBUS ##

We need to add some configuration files for tollgate to DBUS' configuration in order to allow the web server process to use tollgate's backend.

In `example/dbus/system.d/tollgate.conf` are some example configuration you can use with tollgate.  Copy this to `/etc/dbus-1/system.d/`, and modify with the appropriate username that the webserver uses (if it is not `www-data`).

Then reload the DBUS configuration with `/etc/init.d/dbus reload`.

## Create a project ##

Now, you should create a Django project for tollgate to use.  This won't have any of tollgate's code in this folder -- it will reference a the system-installed copy.

    $ django-admin startproject mylanportal

This will create some boilerplate code for a Django site.  Currently, tollgate doesn't support not being at the root of the site, but this may change in the future.

From here on in, I'm going to assume your project name is `mylanportal`.

## Configure the project ##

Jump into the `mylanportal/mylanportal/urls.py`.  Change it so it includes `tollgate.urls`.  `tollgate.urls` will also give you the Django admin site, and the internationalisation configuration app.  It should look something like this:

    from django.conf.urls import patterns, include, url
    urlpatterns = patterns('',
	  (r'^', include('tollgate.urls')),
    )

The next step is to setup `settings.py`.

Near the top, add these lines:

    from os.path import *
	PROJECT_PATH = realpath(dirname(__file__))

This is a handy trick because you can use it to setup other paths later.

Setup the location of the database.  It is recommended you use MariaDB (MySQL).

You should also setup a `STATIC_ROOT` for where all the static files should be served from, and a `STATIC_URL`.  Be aware that if you are deploying on a HTTPS site (which you should!) you need to make your resources also be on a HTTPS site.  The purpose of this is that outside of DEBUG mode, you're expected to serve static files external to Django -- as it is much faster.

To your `MIDDLEWARE_CLASSES`, add `tollgate.frontend.common.TollgateMiddleware`, 

To your `INSTALLED_APPS`, append `south`, `tollgate.api`, `tollgate.frontend`, and `tollgate.scripts`.

You should also add the following extra settings for tollgate and configure appropriately:

    LAN_SUBNET='10.4.0.0/23'
	LAN_IFACE='eth1'
	DEFAULT_QUOTA_AMOUNT=150
	RESET_EXCUSE_REQUIRED=True
	RESET_PURCHASE=False
	ONLY_CONSOLE=False
	RESTRICTED_CALLS_KEY=''
	LOGIN_URL='/login/'
	LOGOUT_URL='/logout/'

The final setting to add is a URL where you are hosting the tollgate sources with your modifications.  You should **never** link back to the official tollgate repository using this method (there is already a link to the official repo on the source page).

Not hosting the source code yourself may expose you to legal liability.

## Configure daemons ##

Install the init scripts and backend configuration:

    $ sudo cp platform/debian/init.d/* /etc/init.d/
	$ sudo cp platform/debian/default/* /etc/default/
	$ sudo mkdir /etc/tollgate/
	$ sudo cp example/tollgate/backend.ini /etc/tollgate/

Modify the scripts (`tollgate-backend` and `tollgate-captivity`) as appropriate to match the path to the tollgate_backend and tollgate_captivity scripts.

Edit `/etc/default/tollgate-captivity` to point to the URL where tollgate is hosted.

To make the daemons start, run:

    $ sudo update-rc.d tollgate-backend defaults
	$ sudo update-rc.d tollgate-captivity defaults

Modify the backend configuration as appropriate for your network (`/etc/tollgate/backend.ini`).
	
We won't start the daemons just yet, though.

## Configure cron ##

tollgate requires a periodic cronjob to refresh the list of hosts in it's database.

An example configuration is given in `examples/tollgate.cron`.  You will need to adapt it to point to the path of your Django project.

## Configure webserver ##

You'll need to now configure your web server.  You may wish to copy `tollgate/tollgate.wsgi` and use it in your own project folder.

There is an example apache2 configuration, including all vhosts, in `example/apache2/tollgate-vhost`.

You will need to modify the path of static items (like the WPAD and WFC vhosts, and aliases for static files) to the appropriate locations, and URLs.

Included in the examples is how to configure a gitweb instance.  You could also push code changes to an external repository, however it must be accessible to users at all times (ie: you should mark it as "unmetered").

## Start the daemons ##

The first time you run you'll need to manually start the daemons.  They will start automatically on next boot.

