from django.core.management.base import BaseCommand
from datetime import datetime
import json
import os

from data_explorer.models import AFSLicenseeEntry


def unpack(lst):
    if len(lst) > 0:
        return lst[0]
    return lst


class Command(BaseCommand):
    help = 'Import Australian Financial Service Licensee data'

    def handle(self, *args, **kwargs):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        afsl2_file_path = os.path.join(current_dir, 'afsl2.json')
        with open(afsl2_file_path, 'r') as data_file:
            company_list = json.load(data_file)
            for company in company_list:
                abn = unpack(company['abn'])
                status = unpack(company['status']) or None
                service_address = unpack(company['service_address']) or None
                license_no = unpack(company['license_no'])
                commenced = unpack(company['commenced']) or None
                name = unpack(company['name'])
                principle_business_address = unpack(company['principle_business_address']) or None
                acn = None
                if '/' in abn:
                    commenced = abn
                    abn = None
                if abn and len(str(abn)) < 11:
                    acn = abn
                    abn = None
                if commenced:
                    commenced = datetime.strptime(commenced, '%d/%m/%Y').date()

                if abn:
                    abn = int(abn.replace(' ', ''))
                if acn:
                    acn = int(acn.replace(' ', ''))

                AFSLicenseeEntry.objects.create(
                    name=name,
                    license_no=int(license_no),
                    abn=abn,
                    acn=acn,
                    commenced_date=commenced,
                    service_address=service_address,
                    status=status,
                    principle_business_address=principle_business_address
                )

