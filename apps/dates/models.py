# Django
from utils.models import ControlInfo
from django.db import models
# users
from apps.users.models import Usuarios
# places
from apps.places.models import Solicitudes

class CitasAgendadas(ControlInfo):
    identifier = 'CITA'
    fecha = models.DateField(editable=False)
    hora = models.TimeField(editable=False)
    usuario = models.ForeignKey(Usuarios, editable=False, on_delete=models.PROTECT, related_name='citas')

    class Meta:
        unique_together = ('fecha', 'hora', 'usuario')