from django.db import models

import os
import uuid

from velo.velo.mixins.models import TimestampMixin


def _get_document_upload_path(instance, filename):
    return os.path.join("tempdocument", str(uuid.uuid4()), filename)


class TempDocument(TimestampMixin, models.Model):
    doc = models.FileField(upload_to=_get_document_upload_path)
