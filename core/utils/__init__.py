import os
import re
from decimal import Decimal
from enum import Enum
from uuid import uuid4

from django.utils.text import slugify as django_slugify


def german_number(number):
    if isinstance(number, float):
        number = f"{number:.2f}".replace(".", ",")
    else:
        number = str(number)
    groups = []
    while number and number[-1].isdigit():
        groups.append(number[-3:])
        number = number[:-3]
    return (number + ".".join(reversed(groups))).replace(".,", ",")


def decimal_to_str(dec):
    """
    Converts scientific notation in decimal conversion to actual floats as string.

    '1E-7' => '0.0000001'
    :param Decimal dec:
    :return str:
    """
    float_string = str(dec)
    if "E" in float_string:  # detect scientific notation
        digits, exp = float_string.split("E")
        digits = digits.replace(".", "").replace("-", "")
        exp = int(exp)
        zero_padding = "0" * (abs(int(exp)) - 1)  # minus 1 for decimal point in the sci notation
        sign = "-" if dec < 0 else ""
        if exp > 0:
            float_string = "{}{}{}.0".format(sign, digits, zero_padding)
        else:
            float_string = "{}0.{}{}".format(sign, zero_padding, digits)
    return float_string


def with_validity(amount, validity=2):
    """

    This ensures that the remaining string is returned with a max of validity digits after the decimal point.

    :param str|Decimal|float|int amount: An amount given as string e.g. '12.123'
    :param validity: int
    :return:
    """
    return decimal_to_str(Decimal(amount).quantize(Decimal('0.' + '0' * (validity - 1) + '1')))


def get_dynamic_filepath(instance, filename):
    """
    You can use this as upload to to get away with (really almost likely) unique filepath's, prefixed with the
    instance class.
    """
    return f"{instance.__class__.__name__.lower()}/{str(uuid4())[:8]}{os.path.splitext(filename)}"


class OnTheFlyObject(dict):
    """
    > foo = OnTheFlyObject(bar='baz')
    > foo.bar
    Yields baz
    """

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            return None

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            return None


def underscore_to_camelcase(text):
    """
    Converts underscore_delimited_text to camelCase.
    Useful for JSON output
    """
    return "".join(word.title() if i else word for i, word in enumerate(text.split("_")))


def camel_case_to_underscore(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def camel_case_to_dash(name):
    return camel_case_to_underscore(name).replace("_", "-")


def slugify(text):
    # fmt: off
    replace = {
        "ü": "ue",
        "Ü": "Ue",
        "ä": "ae",
        "Ä": "Ae",
        "ö": "oe",
        "Ö": "Oe",
        "ß": "ss",
    }
    # fmt: on

    for source, target in replace.items():
        text = text.replace(source, target)
    return django_slugify(text)


class ChoiceEnum(Enum):
    @classmethod
    def as_choices(cls):
        return [(tag.name, tag.value) for tag in cls]

    @classmethod
    def value_from_name(cls, name):
        for tag in cls:
            if tag.name == name:
                return tag.value
        return name

    def __json__(self):
        return self.name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return other == self.name

    def __hash__(self):
        return hash(self.name)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_version(request):
    if not request:
        return 'UnknownClient', 2, 0, 0, 300

    version = request.META.get('HTTP_X_APP_VERSION')

    if not version:
        return 'UnknownClient', 2, 0, 0, 300
    version = version.split(' - ')

    if len(version) > 1:
        user_agent = version[0]
        version = version[1]
    else:
        user_agent = 'MobileClient'
        version = version[0]

    try:
        version_number, count = version.lstrip('v').split('+')
        major, minor, bugfix, count = [int(_) for _ in version_number.split('.')] + [int(count)]
        return user_agent, major, minor, bugfix, count
    except ValueError:
        return user_agent, 1, 0, 0, 1


def is_mobile_client(request):
    user_agent, major, minor, bugfix, count = get_version(request)
    return user_agent.startswith('MobileClient')