# Django
from django import forms
# users
from apps.users.models import Usuarios

class UsersForm(forms.ModelForm):
    repeat_password = forms.CharField(label = 'Confirmar contraseña', widget = forms.PasswordInput())

    class Meta:
        model = Usuarios
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }
        
        error_messages = {
            'email': {
                'unique': 'Este correo electrónico ya fue registrado'
            },
            'phone_number': {
                'unique': 'Este número de teléfono ya fue registrado'
            }
        }

    def clean_repeat_password(self):
        repeat_password = self.cleaned_data['repeat_password']
        if not repeat_password == self.cleaned_data['password']:
            raise forms.ValidationError('La contraseña no coincide', code='invalid')
        return repeat_password
    
    def __init__(self, *args, **kwargs):
        super(UsersForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.setdefault('class', 'form-control')