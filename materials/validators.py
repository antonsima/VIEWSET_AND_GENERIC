import re

from rest_framework.serializers import ValidationError


class VideoURLValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        reg = re.compile("\S+youtube.com\S+")
        tmp_val = dict(value).get(self.field)

        if not bool(reg.match(tmp_val)):
            raise ValidationError('URL видео должен вести на сайт "youtube.com"')
