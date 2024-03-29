# Django
from django.views.generic import TemplateView, CreateView, DetailView, RedirectView
from django.urls import reverse_lazy, reverse
from django.http import Http404
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Sum, Q
from django.conf import settings
# places
from apps.places.models import Solicitudes, Comercios, Validaciones
from apps.places.forms import RequestForm, ShopForm
# dates
from apps.dates.models import CitasAgendadas
from apps.dates.tools import get_dates_from_range, get_times_from_range
# utils
from utils.permissions import UserPermissions
from utils.date import get_date_constancy

dates = get_dates_from_range(settings.START_DATES, settings.END_DATES)
hours = get_times_from_range(settings.START_HOURS, settings.END_HOURS, settings.PERIODS_TIME)

class Main(UserPermissions, TemplateView):
    template_name = 'places/main.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        context['dates'] = self.request.user.citas.order_by('fecha', 'hora')
        return context

class CreateRequest(UserPermissions, SuccessMessageMixin, CreateView):
    template_name = 'places/create.html'
    model = Solicitudes
    form_class = RequestForm
    success_url = reverse_lazy('places:create_request')
    success_message = 'Solicitud creada exitosamente'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return redirect('users:logout')
        all_used_places = Solicitudes.objects.filter(fecha_reg__year=2024).aggregate(places=Sum('cantidad_espacios'))['places']
        used_places = self.request.user.solicitudes.filter(fecha_reg__year=2024).aggregate(places=Sum('cantidad_espacios'))['places']
        self.max_places = settings.LIMIT_PLACES - (used_places or 0)
        if all_used_places == settings.LIMIT_ALL_PLACES:
            messages.warning(request, 'Todos los espacios se han agotado.')
            return redirect('places:main')
        if used_places == settings.LIMIT_PLACES:
            messages.warning(request, 'Ya ha alcanzado el número límite de espacios (3) para sus Comercios.')
            return redirect('places:main')
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        return {'nombre_persona': self.request.user.get_full_name()}
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        self.uuid = form.instance.uuid
        lookup = (Q(curp_txt=form.instance.curp_txt or '123') | Q(rfc_txt=form.instance.rfc_txt or '123'))
        dup = Solicitudes.objects.filter(lookup)
        if form.instance.cantidad_espacios > self.max_places:
            messages.warning(self.request, 'Ha superado el número límite de espacios para sus Comercios.')
            return redirect('places:main')
        if dup.exists():
            messages.warning(self.request, 'Ya existe una solicitud con ese RFC/CURP registrada')
            return redirect('places:main')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        context['max_places'] = self.max_places
        return context

    def get_success_url(self, *args, **kwargs):
        return reverse('places:detail_request', kwargs={'uuid':self.uuid})

class Request(UserPermissions, DetailView):
    template_name = 'places/request.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = self.request.user.solicitudes.all()
        context['dates'] = self.request.user.citas.order_by('fecha', 'hora')
        return context

class ObservationsRequest(UserPermissions, DetailView):
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
    
    def post(self, request, *args, **kwargs):
        request_ = self.get_object()
        last_validation = request_.get_last_unattended_validation()
        if last_validation:
            form = RequestForm(request.POST, request.FILES, instance=request_)
            changed = all(field in form.changed_data for field in last_validation.campos['just_fields'])
            if changed:
                form.is_valid()
                request_.__dict__.update(form.cleaned_data)
                request_.estatus = 'resolved'
                request_.save(update_fields=last_validation.campos['just_fields']+['estatus'])
                last_validation.atendido = True
                last_validation.save()
                Validaciones.objects.create(solicitud=request_, estatus='resolved', validador=request.user.get_full_name())
                messages.success(request, 'Observación solventada exitosamente.')
            else:
                messages.warning(request, 'No se completaron los cambios en los campos observados.')
                return redirect('places:observations_request', request_.uuid)
        return redirect('places:detail_request', request_.uuid)

class ObservationsShop(UserPermissions, DetailView):
    template_name = 'places/observations_shop.html'
    model = Comercios
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_validation = self.object.get_last_unattended_validation()
        if last_validation:
            form = ShopForm(instance=self.object)
            context['form'] = form
            context['obs_fields'] = last_validation.campos['just_fields'] or {}
            context['obs_comments'] = last_validation.campos['field_comments'] or {}
        return context
    
    def post(self, request, *args, **kwargs):
        shop_ = self.get_object()
        last_validation = shop_.get_last_unattended_validation()
        if last_validation:
            form = ShopForm(request.POST, request.FILES, instance=shop_)
            changed = all(field in form.changed_data for field in last_validation.campos['just_fields'])
            if changed:
                form.is_valid()
                shop_.__dict__.update(form.cleaned_data)
                shop_.estatus = 'resolved'
                shop_.save(update_fields=last_validation.campos['just_fields']+['estatus'])
                last_validation.atendido = True
                last_validation.save()
                Validaciones.objects.create(comercio=shop_, estatus='resolved', validador=request.user.get_full_name())
                messages.success(request, 'Observación solventada exitosamente.')
            else:
                messages.warning(request, 'No se completaron los cambios en los campos observados.')
                return redirect('places:observations_shop', shop_.uuid)
        return redirect('places:detail_request', shop_.solicitud.uuid)

class CreateShop(UserPermissions, SuccessMessageMixin, CreateView):
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
        if not self.request.user.citas.exists() and not self.request_.estatus == 'rejected':
            # assing date
            assign = False
            for d in dates:
                if assign: break
                for h in hours:
                    assigned_dates = CitasAgendadas.objects.filter(fecha=d, hora=h)
                    if assigned_dates.count() < settings.ATTENTION_MODULES:
                        CitasAgendadas.objects.create(fecha=d, hora=h, usuario=self.request.user)
                        assign = True
                        messages.success(self.request, 'Cita asignada exitosamente.')
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

class DownloadDateDoc(UserPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            date = CitasAgendadas.objects.get(uuid=kwargs['uuid_date'])
            doc = get_date_constancy(request_, date)
            return doc
        except (Solicitudes.DoesNotExist, CitasAgendadas.DoesNotExist):
            raise Http404()