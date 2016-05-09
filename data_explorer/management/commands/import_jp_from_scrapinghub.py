from django.core.management.base import BaseCommand
from datetime import datetime
import json
import os
from scrapinghub import Connection
import re
from data_explorer.models import JusticeOfPeace


def unpack(lst):
    if len(lst) > 0:
        return lst[0]
    return lst


def is_australian_mobile_number(number):
    return bool(re.match(r'^\(?(?:\+?61|0)(?:(?:2\)?[ -]?(?:3[ -]?[38]|[46-9][ -]?[0-9]|5[ -]?[0-35-9])|3\)?(?:4[ -]?[0-57-9]|[57-9][ -]?[0-9]|6[ -]?[1-67])|7\)?[ -]?(?:[2-4][ -]?[0-9]|5[ -]?[2-7]|7[ -]?6)|8\)?[ -]?(?:5[ -]?[1-4]|6[ -]?[0-8]|[7-9][ -]?[0-9]))(?:[ -]?[0-9]){6}|4\)?[ -]?(?:(?:[01][ -]?[0-9]|2[ -]?[0-57-9]|3[ -]?[1-9]|4[ -]?[7-9]|5[ -]?[018])[ -]?[0-9]|3[ -]?0[ -]?[0-5])(?:[ -]?[0-9]){5})$', str(number)))

def process_nsw(data_obj):
    first_name, last_name = data_obj['name'].rsplit(' ', 1)
    data = {}
    data['first_name'] = first_name
    data['last_name'] = last_name
    data['suburb'] = data_obj.get('suburb', '')

    if data_obj.get('telephone'):
        if is_australian_mobile_number(data_obj['telephone']):
            data['mobile_number'] = data_obj['telephone']
        else:
            data['phone'] = data_obj['telephone']

    data['raw'] = data_obj
    return data

def process_act(data_obj):
    pass

def process_qld(data_obj):
    last_name, first_middlename = str(data_obj['Full Name']).split(',', 1)
    first_middlename = first_middlename.strip()
    if ' ' in first_middlename:
        middle_name, first_name = first_middlename.rsplit(' ', 1)
    else:
        first_name = first_middlename

    data = {}
    data['suburb'] = data_obj.get('Suburb', '')
    data['first_name'] = first_name
    data['state'] = 'QLD'
    data['last_name'] = last_name
    if data_obj.get('Phone'):
        if is_australian_mobile_number(data_obj['Phone']):
            data['mobile_number'] = data_obj['Phone']
        else:
            data['phone'] = data_obj['Phone']

    data['raw'] = data_obj
    return data

def process_sa(data_obj):
    pass

def process_vic(data_obj):
    pass

def process_nt(data_obj):
    pass

def process_wa(data_obj):
    pass




class Command(BaseCommand):
    help = 'Import JusticeOfPeace from scraping hub'

    def add_arguments(self, parser):
        parser.add_argument('--job-id', dest='job_id')
        parser.add_argument('--type', dest='type')

    def handle(self, *args, **kwargs):
        conn = Connection('1a22b051feb8448fa71bb1cc2ea4aa9c')
        project = conn[62659]
        job_id = kwargs['job_id']
        feed_type = kwargs['type']

        processor_maps = {
            'nsw': process_nsw,
            'act': process_act,
            'qld': process_qld,
            'sa':  process_sa,
            'vic': process_vic,
            'nt':  process_nt,
            'wa':  process_wa,
        }
        processor = processor_maps[feed_type]
        if not processor:
            raise Exception('Unknown type {0}'.format(feed_type))

        for item in project.job(job_id).items():
            dict = processor(item)
            JusticeOfPeace.objects.create(**dict)

