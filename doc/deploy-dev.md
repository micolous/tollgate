# Deploying tollgate in development #

In development, you can run and deploy `tollgate` from within a git clone of the repository.  This is the "old" way of deploying tollgate in production, and has since been superceeded.

You can run tollgate in development either out of a WSGI-compatible webserver, or using Django's single-threaded development server.

## Useful Functions ##

### repair_permissions ###

    $ python manage.py repair_permissions

Repairs execute permissions on scripts.

### setup_settings ###

    $ python manage.py setup_settings

Creates a `tollgate/settings/local.py` for your local settings, and configures your `SECRET_KEY`.
