import hashlib
import json
from io import StringIO

import requests
from django.db import models

from user.models import User


class Content(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    binary = models.FileField()
    checksum = models.CharField(max_length=256, unique=True)
    source = models.CharField(choices=(
        ('YT', 'YouTube'),
        ('RAW', 'Raw File'),
    ), max_length=8, default='RAW')

    def get_checksum(self):
        m = hashlib.sha256()
        m.update(self.binary.read())
        return m.hexdigest()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.checksum = self.get_checksum()
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.checksum


class NFT(models.Model):
    content = models.OneToOneField(Content, on_delete=models.CASCADE)
    token_id = models.CharField(unique=True, max_length=256)
    minting_tx = models.CharField(max_length=256)
    uri = models.URLField()

    def get_metadata(self):
        return requests.get(self.uri).json()

    def __str__(self):
        return self.token_id

