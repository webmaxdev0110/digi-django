from __future__ import unicode_literals

from django.conf import settings
import redis
import json
from random import shuffle
import sys

class Job(object):
    """ Base class for job """

    def get_redis_conn(self):
        return redis.StrictRedis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB
        )


    def break_down(self):
        """
        """
        raise NotImplementedError

    def distribute(self, redis_conn=None):
        " push jobs to Redis "

        jobs = self.break_down()
        redis_conn = redis_conn or self.get_redis_conn()
        redis_conn.rpush('task_queue', *jobs)
        sys.stdout.write('Distributed %d jobs into Redis' % len(jobs))


class ASICJob(Job):

    def break_down(self):
        """
        break down the job and returns a deque object of smaller chunks
        """

        project = 'DOSWebCrawler'
        spider = 'asic'
        step = 100

        registers_config = {
            'Australian Financial Services Licensee': {'start_index': 218580, 'end_index': 500000},
            'Australian Financial Services Authorised Representative': {'start_index': 218580, 'end_index': 500000},
            'Credit Representative': {'start_index': 218585, 'end_index': 500000},
            'Credit Licensee': {'start_index': 219610, 'end_index': 500000}
        }
        jobs = []
        for register_name, config in registers_config.items():
            start_index = config['start_index']
            end_index = config['end_index']
            for index in range(start_index, end_index, step):
                job = {
                    'project': project,
                    'spider': spider,
                    'register': register_name,
                    'start_index': index,
                    'end_index': index + step
                }
                jobs.append(json.dumps(job))
        shuffle(jobs)
        return jobs



class JPCrawlingJob(Job):

    def break_down(self):
        """
        break down the job and returns a deque object of smaller chunks
        """

        project = 'DOSWebCrawler'
        spider_names = [
            'act',
            'nsw',
            'nt',
            'qld',
            'sa',
            'vic',
            'wa',
        ]
        jobs = []
        for spider in spider_names:
            job = {
                'project': project,
                'spider': spider,
            }
            jobs.append(json.dumps(job))

        return jobs
