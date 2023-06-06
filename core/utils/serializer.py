from base64 import b64decode
from uuid import uuid4

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64FileField(serializers.FileField):
    """
    A serializer class to accept base64 strings as file
    """

    default_ext = "bin"

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:"):
            file_format, file_str = data.split(";base64,")
            try:
                ext = file_format.split("/")[-1]
            except KeyError:
                ext = self.default_ext
            data = ContentFile(b64decode(file_str), name=str(uuid4())[9:] + "." + ext)
        return super(Base64FileField, self).to_internal_value(data)

    def to_representation(self, value):
        return super().to_representation(value)
