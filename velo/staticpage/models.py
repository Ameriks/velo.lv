from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models
from django.core.urlresolvers import get_script_prefix
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import iri_to_uri
from django.conf import settings
from ckeditor.fields import RichTextField

class StaticPage(models.Model):
    LANGUAGES = (('', '*'), ) + settings.LANGUAGES
    url = models.CharField(_('URL'),
                           max_length=100,
                           db_index=True,
                           validators=[RegexValidator(r'^[-\w/\.~]+$', _("This value must contain only letters, numbers, dots, underscores, dashes, slashes or tildes."))])
    title = models.CharField(_('title'), max_length=200)
    content = RichTextField(_('content'), blank=True)
    enable_comments = models.BooleanField(_('enable comments'), default=False)

    competition = models.ForeignKey('core.Competition', blank=True, null=True)
    ordering = models.IntegerField(default=0)

    is_published = models.BooleanField(default=True)

    language = models.CharField(max_length=10, choices=LANGUAGES, default='', blank=True)

    class Meta:
        verbose_name = _('flat page')
        verbose_name_plural = _('flat pages')
        ordering = ('competition', 'ordering',)

    def __str__(self):
        return "%s -- %s" % (self.url, self.title)

    def get_absolute_url(self):
        # Handle script prefix manually because we bypass reverse()
        return iri_to_uri(get_script_prefix().rstrip('/') + self.url)
