import os

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class CustomUser(AbstractUser):
    def docs_upload_to(self, instance=None):
        if instance:
            return os.path.join("registration_documents", self.username, instance)
        return None

    full_name = models.CharField(max_length=255, null=True)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(120)], default=25)
    email = models.EmailField(unique=True)
    address = models.TextField(null=True)
    contact_number = models.CharField(null=True, max_length=20)
    business_registration_number = models.CharField(null=True, max_length=50)
    registration_document = models.FileField(null=True, upload_to=docs_upload_to)

    def __str__(self):
        return self.username
