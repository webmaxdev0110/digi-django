from celery.task import task


@task
def ping():
    print 'pong'