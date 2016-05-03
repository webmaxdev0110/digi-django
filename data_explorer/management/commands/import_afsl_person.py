from django.core.management.base import BaseCommand
from datetime import datetime
import json
import os

from data_explorer.models import (
    AFSLicenseeEntry,
    AFSAuthorisedRepresentative,
)


def unpack(lst):
    if len(lst) > 0:
        return lst[0]
    return lst


class Command(BaseCommand):
    help = 'Import Australian Financial Service Licensee data'

    def handle(self, *args, **kwargs):
        count = 0
        current_dir = os.path.dirname(os.path.realpath(__file__))
        afsl1_file_path = os.path.join(current_dir, 'afsl1.json')
        with open(afsl1_file_path, 'r') as data_file:
            company_list = json.load(data_file)
            for company in company_list:
                abn = unpack(company['abn'])
                license_no = unpack(company['license_no'])
                commenced = unpack(company['commenced']) or None
                name = unpack(company['name'])
                if '/' in abn:
                    commenced = abn
                    abn = None
                if commenced:
                    commenced = datetime.strptime(commenced, '%d/%m/%Y').date()
                if abn:
                    abn = int(abn.replace(' ', ''))

                licensed_by = None
                if not AFSLicenseeEntry.objects.filter(license_no=license_no).exists():
                    licensed_by = AFSLicenseeEntry.objects.create(
                        name=name,
                        abn=abn,
                        commenced_date=commenced,
                        license_no=license_no
                    )
                else:
                    licensed_by = AFSLicenseeEntry.objects.filter(license_no=license_no).get()

                persons = company['representive_persons']

                for person in persons:
                    AFSAuthorisedRepresentative.objects.create(
                        name=person['name'][0],
                        license_no=person['rep_no'][0],
                        licensed_by=licensed_by
                    )
