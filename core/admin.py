from django.contrib import admin

from django.contrib import admin
from django.utils.safestring import mark_safe

from core.management.commands.mint_nfts import sync_all_nfts
from core.models import Content, NFT

admin.site.site_header = 'Confirmify'


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    def create_nft(self, request, queryset):
        sync_all_nfts(queryset)
        self.message_user(request, 'Ok. Creating NFTs.')

    list_display = ["checksum", 'user', 'source', 'nft']
    actions = [create_nft]

    list_filter = ["user", ]
    readonly_fields = ["checksum"]

    search_fields = ["checksum"]


def get_nft_url(nft):
    return mark_safe(f'<a target="_blank" href="{nft.get_nft_url()}">Link</a>')
get_nft_url.short_description = 'Explorer'


def get_mint_tx(nft):
    return mark_safe(f'<a target="_blank" href="{nft.get_minting_url()}">Link</a>')
get_mint_tx.short_description = 'Mint TX'


def get_uri(nft):
    return mark_safe(f'<a target="_blank" href="{nft.uri}">Metadata</a>')
get_uri.short_description = 'Metadata'


@admin.register(NFT)
class NFTAdmin(admin.ModelAdmin):
    list_display = ["id", get_uri, 'content', get_nft_url, get_mint_tx]

    readonly_fields = ["token_id", "uri"]
    search_fields = ["content__checksum", 'uri']

    def has_delete_permission(self, request, obj=None):
        return False

