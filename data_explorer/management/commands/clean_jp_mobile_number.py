from django.core.management.base import BaseCommand
from datetime import datetime
import json
import os

from django.db.models import Q
from scrapinghub import Connection
import re
from data_explorer.models import JusticeOfPeace



class Command(BaseCommand):
    help = 'Clean JusticeOfPeace from scraping hub'

    def handle(self, *args, **kwargs):
        for jp in JusticeOfPeace.objects.exclude(mobile_number='', phone='').iterator():
            mobile_number = jp.mobile_number
            changed = False

            if mobile_number:
                if mobile_number.startswith('04') or mobile_number.startswith('+614') or mobile_number.startswith('4'):
                    pass
                else:
                    jp.phone = mobile_number
                    jp.mobile_number = ''
                    changed = True

            if jp.phone:
                if jp.phone.startswith('04') or jp.phone.startswith('+614') or jp.phone.startswith('4'):
                    jp.mobile_number = mobile_number
                    jp.phone = ''
                    changed = True

            if changed:
                jp.save()


        for jp in JusticeOfPeace.objects.exclude(mobile_number__isnull=True).exclude(mobile_number='').iterator():
            if not jp.mobile_number.startswith('+'):
                jp.mobile_number = '+61' + jp.mobile_number
                jp.save()
