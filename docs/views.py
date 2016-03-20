from django.views.generic import TemplateView


class DocWebAppHome(TemplateView):
    template_name = 'docs/home.html'