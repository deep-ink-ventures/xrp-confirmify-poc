from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from .serializers import ContentSerializer
from .models import Content
from .serializers import NFTSerializer
from .models import NFT


class ContentViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = ContentSerializer

    def get_queryset(self):
        return Content.objects.all()


class NFTViewSet(ReadOnlyModelViewSet):
    serializer_class = NFTSerializer

    def get_queryset(self):
        return NFT.objects.all()
