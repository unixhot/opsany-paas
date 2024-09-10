from django.db import models
import datetime


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=datetime.datetime.now())
    update_time = models.DateTimeField(auto_now_add=datetime.datetime.now())

    class Meta:
        abstract = True
        ordering = ["-create_time", "-update_time"]

    def __str__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.pk)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self.pk)

    @classmethod
    def create(cls, **kwargs):
        kwargs["create_time"] = datetime.datetime.now()
        kwargs["update_time"] = datetime.datetime.now()
        obj = cls(**kwargs)
        obj.save()
        return obj

    def update(self, **kwargs):
        kwargs['update_time'] = datetime.datetime.now()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()
        return self

    @classmethod
    def fetch_all(cls, **kwargs):
        return cls.objects.filter(**kwargs).order_by("-create_time")

    @classmethod
    def fetch_one(cls, **kwargs):
        return cls.objects.filter(**kwargs).first()
