# Django
from django import forms
from django.forms.fields import FileField
from django.core.exceptions import NON_FIELD_ERRORS
# places
from apps.places.models import Solicitudes, Comercios, Estacionamiento


class ParkingForm(forms.ModelForm):
    class Meta:
        model = Estacionamiento
        fields = '__all__'
        widgets = {
            'zona': forms.Select(attrs={'class': 'select'}),
            'acceso': forms.Select(attrs={'class': 'select'}),
            'no_estacionamiento': forms.Select(attrs={'class': 'select'}),
            'ubicacion': forms.Select(attrs={'class': 'select'})
        }
    
    def __init__(self, *args, **kwargs):
        super(ParkingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.setdefault('class', 'form-control')


class RequestForm(forms.ModelForm):
    class Meta:
        model = Solicitudes
        fields = '__all__'
        widgets = {
            'regimen_fiscal': forms.Select(attrs={'class': 'select'}),
            'estado': forms.Select(attrs={'class': 'select'}),
            'factura': forms.Select(attrs={'class': 'select'})
        }
    
    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            if isinstance(visible.field, FileField):
                visible.field.widget.attrs['accept'] = 'application/pdf'
            visible.field.widget.attrs.setdefault('class', 'form-control')


class ShopForm(forms.ModelForm):
    class Meta:
        model = Comercios
        fields = '__all__'
        widgets = {
            'equipos': forms.TextInput(attrs={'placeholder': 'Ej. Mesas, Estúfas, Hornos, Refrigeradores, etc.'}),
            'voltaje': forms.Select(attrs={'class': 'select'}),
            'giro': forms.Select(attrs={'class': 'select'}),
            'descripcion': forms.Textarea(attrs={'rows': '3'})
        }
    
    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.setdefault('class', 'form-control')
        # new_choices = self.fields['giro'].choices
        # new_choices.remove(('ambulante', 'Comercio Ambulante'))
        # self.fields['giro'].choices = new_choices