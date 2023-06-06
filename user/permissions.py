from rest_framework.permissions import IsAuthenticated


class RequestedAccountIsLoggedInAccountOrAuthIfNotDetail(IsAuthenticated):

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        if not view.detail:
            return True

        if view.kwargs.get('pk').isdigit() and request.user.id == int(view.kwargs['pk']):
            return True
        elif view.kwargs.get('pk') == 'me':
            return True

        return False
