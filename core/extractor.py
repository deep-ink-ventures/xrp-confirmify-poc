from io import BytesIO
from urllib.parse import urlparse

from pytube import YouTube
from rest_framework.exceptions import ValidationError

from core.models import content_checksum


def extract_checksum_by_domain(url):
    domain = urlparse(url).netloc
    extractor = {
        'www.youtube.com': yt_extractor
    }.get(domain)

    if extractor is None:
        raise ValidationError('Unsupported domain')

    return extractor(url)


def yt_extractor(url):
    if 'watch' not in url or not urlparse(url).query:
        raise ValidationError('Unsupported subpage')

    with BytesIO() as tmp_file:
        YouTube(url).streams.first().stream_to_buffer(tmp_file)
        tmp_file.seek(0)
        return content_checksum(tmp_file.read())
