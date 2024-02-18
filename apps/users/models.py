# Django
from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuarios(AbstractUser):
    class Meta:
        ordering = ['-is_superuser', 'date_joined']
        default_permissions = []

    username = models.CharField('Nombre de usuario', max_length = 100, null = True, blank = True, unique=True)
    first_name = models.CharField('Nombre(s)', max_length = 150)
    last_name = models.CharField('Apellidos', max_length = 150)
    email = models.EmailField('Correo electrónico', unique=True)
    phone_number = models.CharField('Número de teléfono', max_length=10)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'username']