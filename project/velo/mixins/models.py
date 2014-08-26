from django.db import models
from save_the_change.mixins import TrackChanges
from django.utils.translation import ugettext_lazy as _


class TimestampMixin(models.Model):
    class Meta:
        abstract = True
    created_by = models.ForeignKey('core.User', related_name='created_%(class)s_set', null=True, blank=True)
    modified_by = models.ForeignKey('core.User', related_name='modified_%(class)s_set', null=True, blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    modified = models.DateTimeField(_('Modified'), auto_now=True, auto_now_add=True)

class StatusMixin(models.Model):
    STATUS_DELETED = -1
    STATUS_INACTIVE = 0
    STATUS_ACTIVE = 1
    STATUSES = (
        (STATUS_INACTIVE, 'Inactive'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_DELETED, 'Deleted'),
    )

    class Meta:
        abstract = True

    status = models.SmallIntegerField(choices=STATUSES, default=STATUS_INACTIVE)


class CustomTrackChanges(TrackChanges):
    @property
    def changed_values(self):
        return self._changed_fields