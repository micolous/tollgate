.. _permissions:

***********************
Permissions in tollgate
***********************

There exists some permissions that are used inside of tollgate.  This documents what they do.

``EventAttendance.can_register_attendance``: Register event attendance
====================================================================

Allows the user to sign in users to the event.  This is done with the "sign in" view.

This will also allow the user to create new users through the sign-in system.

In conjunction with this, there is a UserProfile field called ``maximum_quota_signins`` which controls the maximum amount of quota a user may set when signing in another user.

If set to 0, it will not restrict the quota that may be granted.

If set to greater values, this is the maximum number of megabytes that a user may grant during the sign-in process, and disables use of the unlimited quota option.


``EventAttendance.can_view_quota``: View quota
==============================================

Allows access to the "quota management" view.

This lets the user see a report of all the internet quota used by each user at the event, as well as the overall total for the event.

This also lets the user view all resets performed for a user.


``EventAttendance.can_reset_quota``: Reset quota
================================================

This permission controls the ability to reset another user's quota.

You cannot reset your own quota more than once -- you must get another user to do it for you.

The UI to access this permission also requires you grant ``EventAttendance.can_view_quota``.

In conjuction with this, there is a UserProfile field called ``maximum_quota_resets`` which controls the number of times a user may reset another user's quota.

If set to 0, it will allow the user to reset another user's quota an unlimited number of times.  If set to 1, it will only allow them to perform the regular "one free reset".


``EventAttendance.can_reset_own_quota``: Reset own quota multiple times
=======================================================================

Setting this permission allows a user to reset their own quota multiple times through the quota management interface, so long as it is not in conflict with the ``maximum_quota_resets`` setting.

The UI to access this permission also requires you grant ``EventAttendance.can_view_quota``.


``EventAttendance.can_revoke_access``: Revoke internet access for a user
========================================================================

Allows the user to revoke internet access rights for another user.

The UI to access this permission also requires you grant ``EventAttendance.can_view_quota``.


``EventAttendance.can_change_coffee``: Coffee request access change
===================================================================

This ACL is deprecated and will be removed in a future version.

This controls access to being able to change the ``coffee`` flag for a user.  The UI to set this flag has been removed, so this ACL does nothing.

This is a seperate ACL because of Dasman and Ravenge. ;-)


``IP4PortForward.can_ip4portforward``: Manage IPv4 port forwarding
==================================================================

Allows access to the IPv4 port forwarding interface.


``UserProfile.can_toggle_internet``: Toggle internet access for users
=====================================================================

This permission controls the ability to use the "internet switch" for other users.

The UI to access this permission also requires you grant ``EventAttendance.can_view_quota``.


