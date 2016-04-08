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


class SignupView(TemplateView):

    template_name = 'accounts/signup.html'
