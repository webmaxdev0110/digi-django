from django.views.generic import RedirectView
from form_document.models import FormDocumentLink
from django.conf import settings


class FormTrackingUrlRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        try:
            document_link = FormDocumentLink.objects.get(hash=kwargs['form_link_hash'])
        except FormDocumentLink.DoesNotExist:
            # todo: Redirect to 500 page
            return None

        if not document_link.form_response:
            # Create an empty form response
            response = document_link.form_template.get_or_create_compiled_form().create_empty_response()
            document_link.form_response = response
            document_link.save()
            response_id = response.id
        else:
            response_id = document_link.form_response.pk

        if settings.FRONTEND_PORT == 3000:
            # Development settings
            protocol = 'http'
            port = ':3000'
        else:
            protocol = 'https'
            port = ''

        form_template = document_link.form_template
        redirect_url = '{protocol}://{site_domain}{port}/forms/{form_template_id}/{response_id}'.format(**{
            'protocol': protocol,
            'site_domain': form_template.owner.site.domain,
            'port': port,
            'form_template_id': form_template.pk,
            'response_id': response_id
        })

        # todo: Verify people if link was sent through email

        return redirect_url
