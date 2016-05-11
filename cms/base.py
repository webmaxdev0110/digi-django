"""
Our base representation for different types of page models.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from feincms.admin import item_editor
from feincms.models import create_base_model


class SimplePageManager(models.Manager):

    def published(self):
        """
        Filter by pages that are marked as active/published.
        """
        return self.filter(published=True)

SimplePageAdmin = item_editor.ItemEditor


class SimplePage(create_base_model(inherit_from=models.Model)):
    """
    A simple wrapper on the feincms base model with some common fields
    set for use in implemented types.
    """
    published = models.BooleanField(_('published'), default=False)
    title = models.CharField(_('title'), max_length=100,
        help_text=_('This is used for the generated navigation too.'))

    class Meta(object):
        abstract = True

        verbose_name = _('simple page')
        verbose_name_plural = _('simple pages')

    objects = SimplePageManager()

    def __str__(self):
        return self.title
