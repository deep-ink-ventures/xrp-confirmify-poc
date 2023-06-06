from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated, BasePermission, IsAdminUser


class TwoFactorNotAuthenticated(NotAuthenticated):
    default_detail = "Two Factor Authentication missing."


class TwoFactorProtectedPermission(IsAuthenticated):
    def has_permission(self, request, view):
        is_authenticated = super().has_permission(request, view)
        if is_authenticated and request.user.has_two_factor_enabled():
            if not request.user.has_session_authenticated(request.headers["Authorization"][4:]):
                raise TwoFactorNotAuthenticated()
        return is_authenticated


class IsStaffOrSuperUser(IsAdminUser):

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser) or super().has_permission(request, view)


class ExtendedDjangoModelPermissions(DjangoModelPermissions):
    """
    GET, OPTIONS & HEAD require change rights
    """

    perms_map = {
        "GET": ["%(app_label)s.change_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.change_%(model_name)s"],
        "HEAD": ["%(app_label)s.change_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }


class DownloadPermission:
    """
    Manages a ticket response, where a ticket is a signed response that gives a user limited access to a resource
    for a time frame of 600 secs.
    Therefore, file downloads can request a ticket for a resource and gets a ticket in the response that he can
    use for non-ajax file-downloads.
    """

    MAX_AGE = 100 * 60

    @classmethod
    def create_ticket(cls, unique_string):
        signer = TimestampSigner()
        return signer.sign(unique_string)

    def has_permission(self, request, view):
        if not request.query_params.get("ticket"):
            return False

        # Now check for ticket
        signer = TimestampSigner()
        try:
            signer.unsign(request.query_params["ticket"], max_age=self.MAX_AGE)
            return True
        except SignatureExpired:
            return False
        except BadSignature:
            return False
