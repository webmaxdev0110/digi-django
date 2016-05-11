from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView

from cms.blog.models import BlogEntry


class BlogHomeView(TemplateView):
    """ Simple view to redirect us to the latest blog entry. """

    def get(self, request, *args, **kwargs):
        return Http404()

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
        context.update({
            'entry': self.entry
        })

        return context