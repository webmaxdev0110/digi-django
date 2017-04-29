from django.db.models.query import QuerySet
from django.utils.timezone import now


class ArchiveModelQuerySet(QuerySet):

    def available(self):
        return self.filter(archived_on__isnull=True)

    def archive(self):
        self.update(archived_on=now())
        return self
