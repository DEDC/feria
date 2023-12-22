# Django
from django.views.generic import TemplateView
# places
from apps.places.models import Solicitudes, Comercios
# dates
from apps.dates.models import CitasAgendadas

class Main(TemplateView):
    template_name = 'admin/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = Solicitudes.objects.all().order_by('fecha_reg')
        context['dates'] = CitasAgendadas.objects.all().order_by('fecha', 'hora')
        context['branches'] = Comercios.objects.all().order_by('nombre')
        return context