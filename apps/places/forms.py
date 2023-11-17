# Django
from django import forms
from django.forms.fields import FileField
# places
from apps.places.models import Solicitudes, Comercios

class RequestForm(forms.ModelForm):
    class Meta:
        model = Solicitudes
        fields = '__all__'
        widgets = {
            'regimen_fiscal': forms.Select(attrs={'class': 'select'}),
            'estado': forms.Select(attrs={'class': 'select'})
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
        widgets = {}
    
    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs.setdefault('class', 'form-control')