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
        for jp in JusticeOfPeace.objects.exclude(Q(mobile_number='')|Q(phone='')).iterator():
            mobile_number = jp.mobile_number
            changed = False

            if mobile_number and re.match(r'^(?:\+?61|0)[2-478](?:[ -]?[0-9]){8}$', mobile_number):
                pass
            else:
                jp.phone = mobile_number
                jp.mobile_number = ''
                changed = True

            if jp.phone and re.match(r'^(?:\+?61|0)[2-478](?:[ -]?[0-9]){8}$', jp.phone):
                jp.mobile_number = jp.phone
                changed = True

            if changed:
                jp.save()
