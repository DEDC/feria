# Django
from django.contrib.auth import backends
# App user
# --- models
from .models import Usuarios

class EmailAuthBackend(backends.ModelBackend):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/phone_number pair, then check
    a username/password pair if email failed
    """
    def authenticate(self, request, username=None, password=None):
        """ Authenticate a user based on email address as the user name. """
        try:
            user = Usuarios.objects.get(email = username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Usuarios.DoesNotExist:
            try:
                user = Usuarios.objects.get(phone_number = username)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except Usuarios.DoesNotExist:
                return None