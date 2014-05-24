from django.db import models


class Account(models.Model):
    """
    A test account model.
    """
    name = models.CharField(max_length=64)


class ProxyAccount(Account):
    """
    A model for testing proxy models.
    """
    class Meta:
        proxy = True
