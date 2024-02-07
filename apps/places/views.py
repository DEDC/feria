# Django
from django.forms.models import BaseModelForm
from django.views.generic import TemplateView, CreateView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import Http404, HttpResponse
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
# places
from apps.places.models import Solicitudes, Comercios
from apps.places.forms import RequestForm, ShopForm
# dates
from apps.dates.models import CitasAgendadas

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
        modules = 5
        context = self.get_context_data(**kwargs)
        date = request.POST.get('date')
        time = request.POST.get('time')
        scheduled = CitasAgendadas.objects.filter(fecha=date, hora=time)
        if scheduled.count() < modules:
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
    
    def get_initial(self):
        return {'nombre_persona': self.request.user.get_full_name()}
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        self.uuid = form.instance.uuid
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
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
        return context

    def form_valid(self, form):
        form.instance.solicitud = self.request_
        return super().form_valid(form)
    
    def get_initial(self):
        try:
            self.request_ = Solicitudes.objects.get(uuid=self.kwargs['uuid'])
        except Solicitudes.DoesNotExist:
            raise Http404()
        return {'nombre': self.request_.nombre_comercial}

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('places:detail_request', kwargs={'uuid':self.request_.uuid})