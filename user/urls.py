from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenVerifyView

from .views.user_views import UserViewSet, ProfileBasedTokenView, TokenRefreshView

router = SimpleRouter(trailing_slash=True)
router.register(r'users', UserViewSet, 'user-user')

urlpatterns = router.urls

urlpatterns += [
    path("jwt/create/", ProfileBasedTokenView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
]
