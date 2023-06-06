import json
from io import StringIO
from typing import List

import requests
from django.conf import settings
from xrpl.clients import JsonRpcClient
from xrpl.core.keypairs import generate_seed
from xrpl.models import NFTokenMint
from xrpl.transaction import safe_sign_and_autofill_transaction, send_reliable_submission
from xrpl.utils import str_to_hex
from collections import defaultdict

from core.models import Content, NFT
from user.models import User


def get_client():
    return JsonRpcClient(settings.XRP_RPC_URL)


def sync_all_nfts():
    by_user = defaultdict(list)
    for content in Content.objects.filter(nft__isnull=True).prefetch_related('user'):
        by_user[content.user].append(content)

    client = get_client()
    for user, content_list in by_user.items():
        nft_sync = NFTSync(user, content_list, client)
        nft_sync.sync()


class NFTSync:

    def __init__(self, user: User, content_list: List[Content], client: JsonRpcClient = None):
        self.user = user
        self.client = client or get_client()
        self.wallet = self.user.load_wallet()
        self.content_list = content_list

    def sync(self):
        incrementor = NFT.objects.filter(content__user=self.user).count() + 1
        nfts = []
        for content in self.content_list:
            nfts.append(
                self.mint_nft(content, incrementor)
            )
            incrementor += 1
        NFT.objects.bulk_create(nfts)

    def upload_to_ipfs(self, content):
        meta_file = StringIO()
        meta_file.write(json.dumps({
            "source": content.source,
            "issuer": self.wallet.classic_address,
            "checksum": content.checksum
        }))
        meta_file.seek(0)

        response = requests.post(
            'https://api.nft.storage/upload',
            headers={
                "Authorization": f"Bearer {settings.NFT_STORAGE_API_KEY}"
            },
            data=meta_file.getvalue()
        )

        return f"https://{response.json()['value']['cid']}.ipfs.nftstorage.link/"

    def mint_nft(self, content, incrementor):
        uri = self.upload_to_ipfs(content)
        mint_tx = NFTokenMint(
            account=self.wallet.classic_address,
            nftoken_taxon=incrementor,
            # this is the json file on IPFS
            uri=str_to_hex(uri)
        )

        # Sign mint_tx using the issuer account
        mint_tx_signed = safe_sign_and_autofill_transaction(transaction=mint_tx, wallet=self.wallet, client=self.client)
        mint_tx_result = send_reliable_submission(transaction=mint_tx_signed, client=self.client).result
        return NFT(
            content=content,
            token_id=mint_tx_result['meta']['nftoken_id'],
            minting_tx=mint_tx_result['hash'],
            uri=uri
        )
