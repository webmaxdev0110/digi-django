from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from feincms.content.image.models import ImageContent
from feincms.content.raw.models import RawContent
from feincms.content.richtext.models import RichTextContent

from accounts.models import User
from cms.base import (
    SimplePageManager,
    SimplePage,
)


class EntryManager(SimplePageManager):

    def published(self):
        """
        Filter entries by those that are expected to be visible given the date.
        """
        qs = super(EntryManager, self).published()
        return qs.filter(published_on__isnull=False, published_on__lte=timezone.now())


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/avatars/{1}'.format(instance.user.pk, filename)


class BlogEntry(SimplePage):

    hero_image = models.ImageField(upload_to=user_directory_path, null=True)
    user = models.ForeignKey(User, null=True)
    published_on = models.DateTimeField(null=True,
        help_text=_('The date on which the blog entry is visible.'))
    excerpt = models.TextField(blank=True, null=True,
        help_text=_('Add a brief excerpt summarizing the content of this page.'))
    slug = models.SlugField(max_length=100)

    class Meta(object):
        get_latest_by = 'published_on'
        ordering = ['-published_on']

        verbose_name = _('blog entry')
        verbose_name_plural = _('blog entries')

    objects = EntryManager()

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.published and not self.published_on:
            self.published_on = timezone.now()
        super(BlogEntry, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cms_blog', kwargs = {'slug': self.slug})


BlogEntry.register_templates({
    'title': _('Blog'),
    'path': 'blog/article.html',
    'regions': (
            ('body', _('Content Area')),
        ),
    })

BlogEntry.create_content_type(RichTextContent)
BlogEntry.create_content_type(RawContent)
BlogEntry.create_content_type(ImageContent)