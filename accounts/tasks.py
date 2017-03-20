from django.core.urlresolvers import reverse
from accounts.models import User
from emails.apis import send_account_email_verification_email
from emondo.celery import app



@app.task
def send_user_activation_email(user_id):
    user = User.objects.get(pk=user_id)
    user.ensure_activation_code_exists()
    activation_link = reverse(
        'account_email_activation',
        args=(user.email, user.activation_code,)
    )
    send_account_email_verification_email(
        user.email,
        activation_link
    )


