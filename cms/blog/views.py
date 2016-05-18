import random

from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.syndication.views import Feed

from cms.blog.models import BlogEntry


class BlogHomeView(ListView):
    """ Simple view to redirect us to the latest blog entry. """
    models = BlogEntry
    context_object_name = 'entries'
    paginate_by = 8
    template_name = 'blog/blog_home.html'

    def get_queryset(self):
        return self.models.objects.published().order_by('-published_on')

    def get_context_data(self, **kwargs):
        context = super(BlogHomeView, self).get_context_data(**kwargs)
        tag_lines = [
            ('Create simple, human-like, conversational forms  that autofill your existing documents',
             'emondo is the world\'s most secure platform for your clients to sign like Steve Jobs, '
             'witness, complete, and certify documents online. '
             'Instantly identify your clients in over 30 countries and stamp on the '
             'Blockchain. Get your free account today!',),
        ]
        context['tagline_index'] = random.randint(0, len(tag_lines) - 1)
        return context


class BlogDetailView(TemplateView):
    """ Our view to set the template path prior to a regular get request. """

    def get(self, request, *args, **kwargs):
        """
        Here we base our render on the selected template/blog entry.
        """

        # Not the prettiest thing - we set the instance member based on which blog
        # we are getting - the template can differ from blog to blog.
        blog = get_object_or_404(BlogEntry, slug=kwargs.get('slug', None))
        self.template_name = blog.template.path
        self.entry = blog
        return super(BlogDetailView, self).get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        """
        Set the blog entry context.
        """

        context = super(BlogDetailView, self).get_context_data(**kwargs)
        tag_lines = [
            ('Create simple, human-like, conversational forms  that autofill your existing documents',
             'emondo is the world\'s most secure platform for your clients to sign like Steve Jobs, '
             'witness, complete, and certify documents online. '
             'Instantly identify your clients in over 30 countries and stamp on the '
             'Blockchain. Get your free account today!',),
        ]
        context.update({
            'entry': self.entry,
            'tagline_index': random.randint(0, len(tag_lines) - 1)
        })

        return context


class BlogFeed(Feed):
    """ RSS Feed Class """
    title = "Emondo blog feed"
    link = "/blog/feed"
    description = "Emondo blog feed"

    def items(self):
        return BlogEntry.objects.published().order_by('-published_on')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt

    def item_link(self, item):
        return reverse('cms_blog', args=[item.slug])

