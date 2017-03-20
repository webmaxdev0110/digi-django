import hashlib
import random


def gen_email_activation_code(email):
    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
    if isinstance(email, unicode):
        email = email.encode('utf-8')
    activation_key = hashlib.sha1(salt + email).hexdigest()
    return activation_key