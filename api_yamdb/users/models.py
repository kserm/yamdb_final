from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from users.validators import validate_name_me


class User(AbstractUser):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    ROLE_CHOICES = (
        (USER, "User"),
        (MODERATOR, "Moderator"),
        (ADMIN, "Admin"),
    )

    unicode_username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        validators=(
            validate_name_me,
            unicode_username_validator
        ),
        unique=True,
        max_length=150
    )
    email = models.EmailField(
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        blank=True
    )
    role = models.CharField(
        max_length=150,
        choices=ROLE_CHOICES,
        default="user")

    @property
    def is_admin(self):
        return (self.role == self.ADMIN
                or self.is_superuser)

    @property
    def is_moderator(self):
        return (self.role == self.MODERATOR
                or self.is_staff)
