from django.db import models
from datetime import datetime


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    update_time = models.DateTimeField(auto_now_add=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    class Meta:
        abstract = True
        ordering = ["-create_time", "-update_time"]

    def __str__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.pk)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.pk)

    @classmethod
    def create(cls, **kwargs):
        obj = cls(**kwargs)
        obj.save()
        return obj

    def update(self, **kwargs):
        kwargs['update_time'] = datetime.now()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()
        return self

    @classmethod
    def fetch_all(cls, **kwargs):
        return cls.objects.filter(**kwargs)

    @classmethod
    def counter(cls, **kwargs):
        query_set = cls.fetch_all(**kwargs)
        return query_set.count()

    @classmethod
    def pagination(cls, page=1, per_page=10, order_by='-create_time', exclude={}, **kwargs):
        query_set = cls.fetch_all(**kwargs).exclude(**exclude)
        total = query_set.count()
        query_set = query_set.order_by(order_by)

        current_page = query_set[(page-1) * per_page: page * per_page]
        return current_page, total

    @classmethod
    def fetch_one(cls, **kwargs):
        return cls.objects.filter(**kwargs).first()

    @classmethod
    def find_by_pk(cls, pk):
        return cls.objects.get(pk=pk)

    @classmethod
    def find_by_pks(cls, pks):
        return cls.objects.filter(pk__in=pks)
