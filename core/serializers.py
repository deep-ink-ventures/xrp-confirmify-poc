from rest_framework import serializers
from .models import Content
from .models import NFT
from .utils.serializer import Base64FileField


class ContentSerializer(serializers.ModelSerializer):

    binary = Base64FileField()

    class Meta:
        model = Content
        fields = ('id', 'binary', 'checksum', 'source', 'user')
        read_only_fields = ('id', 'checksum', 'source')


class NFTSerializer(serializers.ModelSerializer):
    metadata = serializers.SerializerMethodField()

    @staticmethod
    def get_metadata(nft: NFT):
        return nft.get_metadata()

    class Meta:
        model = NFT
        fields = ('id', 'content', 'token_id', 'minting_tx', 'metadata')
