from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from .extractor import extract_checksum_by_domain
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

    @action(["post"], detail=False)
    def verify(self, request, *args, **kwargs):
        """Expects a post body with a URL"""
        checksum = extract_checksum_by_domain(request.data.get('url'))
        try:
            content = Content.objects.get(checksum=checksum, nft__isnull=False)
            return Response(status=HTTP_200_OK, data=NFTSerializer(content.nft).data)
        except Content.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)

    def get_queryset(self):
        return Content.objects.all()


class NFTViewSet(ReadOnlyModelViewSet):
    serializer_class = NFTSerializer

    def get_queryset(self):
        return NFT.objects.all()
