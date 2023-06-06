from rest_framework.routers import SimpleRouter
from .views import ContentViewSet
from .views import NFTViewSet


router = SimpleRouter(trailing_slash=True)
router.register(r'contents', ContentViewSet, 'core-content')
router.register(r'nfts', NFTViewSet, 'core-nft')

urlpatterns = router.urls
