from django.db import models


class Account(models.Model):
    """
    A test account model.
    """
    name = models.CharField(max_length=64)
