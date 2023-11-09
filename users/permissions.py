from decouple import config
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny, BasePermission


class NotLoggedInPermission(AllowAny):
    """used when user not logged in (like verify email address)"""
    message = 'Permission Denied'

    def has_permission(self, request, view):
        """By default, headers key are been changed from
        ESTATEIQ_HEADER to EstateIQ-Sk-Header that's why we change the key """
        for key, value in request.headers.items():
            #  check the host if we are running manage.py test and if it's on test
            #  mode we allow without the headers .
            #  Note if we pass in headers it provides errors with throttle_scope
            if request.get_host() == "testserver":
                return True
            if key.lower() == 'estateiq-sk-header':
                teems_sk_header = request.headers['EstateIQ-Sk-Header']
                is_header = teems_sk_header == config('ESTATEIQ_SK_HEADER')
                return is_header


class LoggedInPermission(BasePermission):
    """
    Used when the user is logged in we only added this if other verification
    could be needed but right now we are only using the secret header
    """
    message = "Permission Denied or Email not verified"

    def has_permission(self, request, view):
        """By default, headers key are been changed from
                ESTATEIQ_HEADER to EstateIQ-Sk-Header that's why we change the key """
        # check first  if the user is not authenticated
        if not request.user.is_authenticated:
            return False
        if not request.user.verified:
            raise ParseError(
                {"error": "Your email address has not been verified. Check your inbox for the verification link."})
        for key, value in request.headers.items():
            #  check the host if we are running manage.py test and if it's on test
            #  mode we allow without the headers .
            #  Note if we pass in headers it provides errors with throttle_scope
            if request.get_host() == "testserver":
                return True
            if key.lower() == 'estateiq-sk-header':
                estateiq_sk_header = request.headers['EstateIQ-Sk-Header']
                is_header = estateiq_sk_header == config('ESTATEIQ_SK_HEADER')
                return is_header


class LoggedInStaffPermission(BasePermission):
    message = "You don't have permission you must be a staff user"

    def has_permission(self, request, view):
        """By default, headers key are been changed from
                ESTATEIQ_HEADER to EstateIQ-Sk-Header that's why we change the key """
        #  if the user is not authenticated
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        if request.user.is_superuser:
            return True
        if not request.user.is_superuser:
            if not request.user.is_staff:
                raise ParseError(
                    {"error": "You don't have permission you must be a staff user."})
