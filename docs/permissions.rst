.. _permissions:

***********************
Permissions in tollgate
***********************

There exists some permissions that are used inside of tollgate.  This documents what they do.

``EventAttendance.can_register_attendance``: Register event attendance
====================================================================

Allows the user to sign in users to the event.  This is done with the "sign in" view.

This will also allow the user to create new users through the sign-in system.


``EventAttendance.can_view_quota``: View quota
============================================

Allows access to the "quota management" view.

This lets the user see a report of all the internet quota used by each user at the event, as well as the overall total for the event.

This also lets the user view all resets performed for a user.


``EventAttendance.can_reset_quota``: Reset quota
==============================================

This permission controls the ability to reset another user's quota.

You cannot reset your own quota more than once -- you must get another user to do it for you.

The UI to access this permission also requires you grant `EventAttendance.can_view_quota`.


``EventAttendance.can_change_coffee``: Coffee request access change
=================================================================

This ACL is deprecated and will be removed in a future version.

This controls access to being able to change the `coffee` flag for a user.  The UI to set this flag has been removed, so this ACL does nothing.

This is a seperate ACL because of Dasman and Ravenge. ;-)


``UserProfile.can_toggle_internet``: Toggle internet access for users
===================================================================

This permission controls the ability to use the "internet switch" for other users.

The UI to access this permission also requires you grant `EventAttendance.can_view_quota`.


