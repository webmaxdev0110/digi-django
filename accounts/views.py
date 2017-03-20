# Create your views here.
from django.views.generic import (
    FormView,
    TemplateView,
)


#
# class LoginView(FormView):
#     """
#     View that allows users to log in to the site.
#     """
#     # form_class = LoginForm
#
#     template_name = 'accounts/login.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(LoginView, self).get_context_data(**kwargs)
#         return context
#
#     # def form_valid(self, form):
#     #     """
#     #     When form is valid, login the user.
#     #     """
#     #
#     #     assert form.user, "After successful LoginForm.clean(), "\
#     #                       "form.user should be set"
#     #     user = form.user
#     #
#     #     if 'ckb-remember-me' not in self.request.POST:
#     #         # Log user out once the browser is closed
#     #         self.request.session.set_expiry(0)
#     #
#     #     # Actually logs the user in
#     #     login(self.request, user)
#     #
#     #     # Redirect somewhere appropriate for this user
#     #     return get_login_redirect(self.request)
#     #
from accounts.models import User


class SignupView(TemplateView):

    template_name = 'accounts/signup.html'


class AccountActivationView(TemplateView):

    template_name = 'accounts/email_activation.html'

    def get_context_data(self, **kwargs):
        context = super(AccountActivationView, self).get_context_data(**kwargs)
        email = kwargs.get('email', '')
        activation_code = kwargs.get('activation_code', '')
        users = User.objects.filter(email=email, activation_code=activation_code)

        is_activation_successful = False
        if users.exists():
            user = users[0]
            user.is_active = True
            user.activation_code = ''
            user.save()
            is_activation_successful = True

        context.update({
            'is_activation_successful': is_activation_successful
        })
        return context