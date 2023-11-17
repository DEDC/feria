from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy

class AdminPermissions(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('users:login')
    redirect_field_name = 'next'

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False

class UserPermissionsWH(AdminPermissions):
    def test_func(self):
        if not self.request.user.is_superuser and self.request.user.user_type == 'almacen':
            return True
        return False

class UserPermissionsUO(AdminPermissions):
    def test_func(self):
        if not self.request.user.is_superuser and self.request.user.user_type == 'unidad':
            return True
        return False