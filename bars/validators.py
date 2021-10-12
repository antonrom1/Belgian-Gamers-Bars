from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_zip_code(value):
    if not 1000 <= value < 10000:
        raise ValidationError(_('Un code postal Belge doit être composé de 4 chiffres'))
