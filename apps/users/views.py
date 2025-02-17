# Django
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import reverse_lazy
# users
from apps.users.forms import UsersForm


class LoginUser(LoginView):
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('places:main')

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return reverse_lazy('admin:main')
        else:
            return reverse_lazy('places:main')


class LogoutUser(LogoutView):
    next_page = '/'


class CreateUser(CreateView):
    template_name = 'usuarios/registro.html'
    form_class = UsersForm
    success_url = reverse_lazy('users:login')
    
    def form_valid(self, form):
        form.instance.set_password(form.instance.password)    
        return super().form_valid(form)

# PasswordReset
class CustomPasswordResetView(PasswordResetView): #envía el token
    template_name = 'usuarios/reset_password/password_reset_form.html'
    email_template_name = 'usuarios/reset_password/password_reset_email.html'
    html_email_template_name = 'usuarios/reset_password/password_reset_email.html'
    subject_template_name = 'usuarios/reset_password/password_reset_subject.txt'
    title = 'Restablezca su contraseña'
    success_url = 'password_reset_done'

class CustomPasswordResetConfirmView(PasswordResetConfirmView): #recibe el token
    template_name = 'usuarios/reset_password/password_reset_confirm.html'
    success_url = reverse_lazy('users:login')
    post_reset_login = True

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'usuarios/reset_password/password_reset_done.html'