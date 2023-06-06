from django.urls import reverse

from core.models import Content, NFT
from core.ripple import sync_all_nfts
from core.utils.test_utils import B64_IMAGE
from user.tests import UserAwareTestCase


class CoreTestCase(UserAwareTestCase):
    editable_models = (Content,)

    def test_content_upload(self):
        self.equip_with_permissions()
        response = self.client.post(reverse('core-content-list'), data={
            'binary': B64_IMAGE,
        })
        self.assertEquals(response.status_code, 201)

        payload = response.json()
        self.assertEquals('d8d2d305f2a98a7813b653a8ce43d331f9911ebbdfd2e42cd0e837e69fb74bd4', payload['checksum'])
        self.assertEquals('RAW', payload['source'])
        self.assertEquals(self.standard_user.id, payload['user'])

    def test_functional_sync_nfts(self):
        self.equip_with_permissions()
        self.client.post(reverse('core-content-list'), data={
            'binary': B64_IMAGE,
        })
        self.assertEquals(0, NFT.objects.count())
        sync_all_nfts()
        self.assertEquals(1, NFT.objects.count())

        nft = NFT.objects.first()
        metadata = nft.get_metadata()
        self.assertEquals(metadata['source'], 'RAW')
        self.assertEquals(metadata['issuer'], self.standard_user.wallet_address)
        self.assertEquals(metadata['checksum'], nft.content.checksum)



