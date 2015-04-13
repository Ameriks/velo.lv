from django.db import models

# Create your models here.
from velo.mixins.models import TimestampMixin
import os
import uuid


def _get_document_upload_path(instance, filename):
    return os.path.join("tempdocument", str(uuid.uuid4()), filename)


class TempDocument(TimestampMixin, models.Model):
    doc = models.FileField(upload_to=_get_document_upload_path)