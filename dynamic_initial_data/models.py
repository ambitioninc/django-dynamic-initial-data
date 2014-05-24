from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from manager_utils import ManagerUtilsManager


class RegisteredForDeletionReceipt(models.Model):
    """
    Specifies a receipt of a model object that was registered for deletion by the dynamic
    initial data process.
    """
    # The model object that was registered
    model_obj_type = models.ForeignKey(ContentType)
    model_obj_id = models.PositiveIntegerField()
    model_obj = generic.GenericForeignKey('model_obj_type', 'model_obj_id', for_concrete_model=False)

    # The time at which it was registered for deletion
    register_time = models.DateTimeField()

    # Use manager utils for bulk updating capabilities
    objects = ManagerUtilsManager()

    class Meta:
        unique_together = ('model_obj_type', 'model_obj_id')
