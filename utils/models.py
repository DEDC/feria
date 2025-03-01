# Python
import uuid
import os
# Django
from django.db import models


class ControlInfo(models.Model):
    class Meta:
        ordering = ['-fecha_reg']

    identifier = ''
    uuid = models.UUIDField(default = uuid.uuid4, editable = False, unique = True)
    folio = models.CharField(max_length = 25, unique = True, null = True, editable = False)
    fecha_reg = models.DateTimeField(auto_now_add = True)
    fecha_mod = models.DateTimeField(auto_now = True)
    activo = models.BooleanField(default = True, editable = False)

    def save(self, *args, **kwargs):
        self.identifier = '{}-{}'.format(self.identifier, str(self.uuid).upper()[:8])
        if not self.folio:
          self.folio = self.identifier
        super(ControlInfo, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class UploadTo:

  def __init__(self, name, folder_name):
    self.name = name
    self.folder_name = folder_name

  def __call__(self, instance, filename):
    extfile = filename.split('.')[-1]
    return '{}/{}_{}.{}'.format(self.folder_name, self.name, instance.folio, extfile)

  def deconstruct(self):
    return ('utils.models.UploadTo', [self.name, self.folder_name], {})


def _delete_file(path):
   """ Deletes file from filesystem. """
   if os.path.isfile(path):
       os.remove(path)