# Django
from django.views.generic import TemplateView, CreateView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Sum
from django.conf import settings
# places
from apps.places.models import Solicitudes, Comercios
from apps.places.forms import RequestForm, ShopForm
# dates
from apps.dates.models import CitasAgendadas
from apps.dates.tools import get_dates_from_range, get_times_from_range

dates = get_dates_from_range(settings.START_DATES, settings.END_DATES)
hours = get_times_from_range(settings.START_HOURS, settings.END_HOURS, settings.PERIODS_TIME)

class Main(TemplateView):
    template_name = 'places/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        context['dates'] = self.request.user.citas.order_by('fecha', 'hora')
        return context

class Dates(TemplateView):
    template_name = 'places/dates.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            self.request_ = Solicitudes.objects.get(uuid=self.kwargs['uuid'])
        except Solicitudes.DoesNotExist:
            raise Http404()
        context['dates'] = self.request.user.citas.order_by('fecha', 'hora')
        context['request_'] = self.request_
        return context
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        date = request.POST.get('date')
        time = request.POST.get('time')
        scheduled = CitasAgendadas.objects.filter(fecha=date, hora=time)
        if scheduled.count() < settings.ATTENTION_MODULES:
            CitasAgendadas.objects.create(fecha=date, hora=time, usuario=request.user)
            messages.success(request, 'Cita agendada exitosamente')
            return redirect('places:detail_request', self.request_.uuid)
        return self.render_to_response(context)

class CreateRequest(SuccessMessageMixin, CreateView):
    template_name = 'places/create.html'
    model = Solicitudes
    form_class = RequestForm
    success_url = reverse_lazy('places:create_request')
    success_message = 'Solicitud creada exitosamente'

    def dispatch(self, request, *args, **kwargs):
        used_places = self.request.user.solicitudes.filter(fecha_reg__year=2024).aggregate(places=Sum('cantidad_espacios'))['places']
        self.max_places = settings.LIMIT_PLACES - (used_places or 0)
        if used_places == settings.LIMIT_PLACES:
            messages.warning(request, 'Ya ha alcanzado el número límite de lugares (3) para sus Comercios')
            return redirect('places:main')
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {'nombre_persona': self.request.user.get_full_name()}
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        self.uuid = form.instance.uuid
        if form.instance.cantidad_espacios > self.max_places:
            messages.warning(self.request, 'Ha superado el número límite de lugares para sus Comercios')
            return redirect('places:main')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        context['max_places'] = self.max_places
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('places:detail_request', kwargs={'uuid':self.uuid})

class Request(DetailView):
    template_name = 'places/request.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        context['dates'] = self.request.user.citas.order_by('fecha', 'hora')
        return context

class ObservationsRequest(DetailView):
    template_name = 'places/observations.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_validation = self.object.get_last_unattended_validation()
        if last_validation:
            form = RequestForm(instance=self.object)
            context['form'] = form
            context['obs_fields'] = last_validation.campos['just_fields'] or {}
            context['obs_comments'] = last_validation.campos['field_comments'] or {}
        return context

class CreateShop(SuccessMessageMixin, CreateView):
    template_name = 'places/create_shop.html'
    model = Comercios
    form_class = ShopForm
    request_ = None
    success_message = 'Comercio creado exitosamente'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_'] = self.request_
        context['shops'] = Comercios.objects.filter(solicitud__usuario=self.request.user)
        try:
            self.request_ = Solicitudes.objects.get(uuid=self.kwargs['uuid'])
        except Solicitudes.DoesNotExist:
            raise Http404()
        return context

    def form_valid(self, form):
        form.instance.solicitud = self.request_
        if not self.request.user.citas.exists():
            # assing date
            assign = False
            for d in dates:
                if assign: break
                for h in hours:
                    assigned_dates = CitasAgendadas.objects.filter(fecha=d, hora=h)
                    if assigned_dates.count() < settings.ATTENTION_MODULES:
                        CitasAgendadas.objects.create(fecha=d, hora=h, usuario=self.request.user)
                        assign = True
                        messages.success(self.request, 'Cita asignada exitosamente')
                        break
        return super().form_valid(form)
    
    def get_initial(self):
        try:
            self.request_ = Solicitudes.objects.get(uuid=self.kwargs['uuid'])
        except Solicitudes.DoesNotExist:
            raise Http404()
        return {}

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('places:detail_request', kwargs={'uuid':self.request_.uuid})