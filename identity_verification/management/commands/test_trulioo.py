
from django.core.management.base import BaseCommand
from identity_verification.trulioo import TruliooRequestBuilder


class Command(BaseCommand):
    help = 'Testing the connection to Trulioo'

    def handle(self, *args, **options):
        builder = TruliooRequestBuilder()
        print(builder.test_connection())
        print(builder.test_authorization())
        print('Expected to see Connection_Succeed and the api account name in two lines')
