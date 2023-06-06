from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from .serializers import ContentSerializer
from .models import Content
from .serializers import NFTSerializer
from .models import NFT


class ContentViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = ContentSerializer

    def create(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload['user'] = request.user.id
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        return Content.objects.all()


class NFTViewSet(ReadOnlyModelViewSet):
    serializer_class = NFTSerializer

    def get_queryset(self):
        return NFT.objects.all()
