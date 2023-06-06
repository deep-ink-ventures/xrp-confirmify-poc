# coding=utf-8
from collections import defaultdict
from time import sleep

from django.core.management.base import BaseCommand

from core.models import Content, NFT
from core.ripple import get_client, NFTSync


def sync_all_nfts(queryset=None):
    queryset = queryset or Content.objects.all()
    by_user = defaultdict(list)
    for content in queryset.filter(nft__isnull=True).prefetch_related('user'):
        by_user[content.user].append(content)

    client = get_client()
    for user, content_list in by_user.items():
        nft_sync = NFTSync(user, content_list, client)
        nft_sync.sync()


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        while True:
            try:
                print("Syncing nfts ...")
                current_count = NFT.objects.count()
                sync_all_nfts()
                new_count = NFT.objects.count()
                print(f"Minted {new_count - current_count} NFT(s) ...\n")
            except Exception as exc:
                print(exc)
            sleep(5)
