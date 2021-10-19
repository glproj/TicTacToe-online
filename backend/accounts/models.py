from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    username_validator = UnicodeUsernameValidator()
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(
    _('username'),
    max_length=150,
    help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
    validators=[username_validator],
    error_messages={
        'unique': _("A user with that username already exists."),
    },
    blank=True,
)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS= ['username']