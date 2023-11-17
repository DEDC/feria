# Django
from django.views.generic import TemplateView, CreateView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.contrib.messages.views import SuccessMessageMixin
# places
from apps.places.models import Solicitudes, Comercios
from apps.places.forms import RequestForm, ShopForm

class Main(TemplateView):
    template_name = 'places/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        return context

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