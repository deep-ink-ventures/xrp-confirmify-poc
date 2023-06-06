from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.views import exception_handler


def rest_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(detail={"error": exc.messages})
    return exception_handler(exc, context)

