# Django
from django.views.generic import TemplateView, DetailView, UpdateView, RedirectView, ListView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import Http404
from rest_framework import status
# DjangoRestFramework
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
# places
from apps.places.models import Solicitudes, Comercios, Validaciones, Lugares
from apps.places.forms import RequestForm, ShopForm
# dates
from apps.dates.models import CitasAgendadas
# utils
from utils.naves import nave1, nave3, zona_a
from utils.permissions import AdminPermissions
from utils.date import get_date_constancy

class Main(AdminPermissions, TemplateView):
    template_name = 'admin/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['requests'] = Solicitudes.objects.all().order_by('fecha_reg')
        context['dates'] = CitasAgendadas.objects.all().order_by('fecha', 'hora')
        context['branches'] = Comercios.objects.all().order_by('nombre')
        return context

class ListRequests(AdminPermissions, ListView):
    model = Solicitudes
    paginate_by = 30
    template_name = 'admin/list_requests.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        requests = Solicitudes.objects.all()
        context['total'] = requests
        context['validated'] = requests.filter(estatus='validated')
        context['rejected'] = requests.filter(estatus='rejected')
        context['pending'] = requests.filter(estatus='pending')
        context['not_assign'] = requests.filter(estatus='')
        context['q'] = self.request.GET.get('q', '')
        context['e'] = self.request.GET.get('e', '')
        print(context)
        return context
    
    def get_queryset(self):
        queryset = self.model._default_manager.all()
        q = self.request.GET.get('q', None)
        e = self.request.GET.get('e', None)
        if q:
            lookup = (Q(pk__icontains=q)|Q(nombre__icontains=q)|Q(folio__icontains=q)|Q(comercio__nombre__icontains=q)|Q(usuario__first_name__icontains=q)|Q(usuario__last_name__icontains=q))
            queryset = queryset.filter(lookup)
        if e:
            if e == 'noassign':
                queryset = queryset.filter(estatus='')
            elif e in ['validated', 'rejected', 'resolved', 'pending']:
                queryset = queryset.filter(estatus=e)
        return queryset.order_by('pk')

class UpdateRequest(AdminPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_request.html'
    model = Solicitudes
    form_class = RequestForm
    success_message = 'Solicitud actualizada exitosamente'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_request', kwargs={'uuid':self.object.uuid})

class UpdateShop(AdminPermissions, SuccessMessageMixin, UpdateView):
    template_name = 'admin/update_shop.html'
    model = Comercios
    form_class = ShopForm
    success_message = 'Comercio actualizada exitosamente'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('admin:update_shop', kwargs={'uuid':self.object.uuid})

class Request(AdminPermissions, DetailView):
    template_name = 'admin/request.html'
    model = Solicitudes
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        request_ = self.get_object()
        if 'validated' in request.POST:
            request_.estatus = 'validated'
            request_.save()
            Validaciones.objects.create(solicitud=request_, estatus='validated', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'rejected' in request.POST:
            request_.estatus = 'rejected'
            lookup = (~Q(estatus='rejected'))
            sib_req = Solicitudes.objects.filter(lookup, usuario=request_.usuario).exclude(uuid=request_.uuid)
            if not sib_req.exists():
                # quitar cita
                date = request_.usuario.citas.first()
                if date:
                    messages.warning(request, 'La Cita {} - {} fue liberada.'.format(date.fecha, date.hora))
                    date.delete()
            request_.save()
            Validaciones.objects.create(solicitud=request_, estatus='rejected', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'pending' in request.POST:
            validation_fields = ['factura', 'regimen_fiscal', 'nombre', 'nombre_replegal', 'rfc_txt', 'curp_txt', 'calle', 'no_calle', 'colonia', 'codigo_postal', 'estado', 'municipio', 'constancia_fiscal', 'comprobante_domicilio', 'acta_constitutiva', 'identificacion', 'curp']
            data = {
                'just_fields': [],
                'field_comments': {}
            }
            for f in request.POST:
                if f in validation_fields:
                    if not request.POST.get(f).strip() == '':
                        data['just_fields'].append(f)
                        data['field_comments'][f] = request.POST.get(f).strip()
            if data['just_fields']:
                request_.estatus = 'pending'
                request_.save()
                Validaciones.objects.create(solicitud=request_, estatus='pending', validador=request.user.get_full_name(), campos=data)
                messages.success(request, 'Estatus asignado exitosamente.')
            else:
                messages.warning(request, 'No se realizó ninguna acción. No se detectaron campos validados.')
        return redirect('admin:request', request_.uuid)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_places = []
        places_price = 0
        places = {'n_1': nave1, 'n_3': nave3, 'z_a': zona_a}
        for p in self.object.solicitud_lugar.filter(fecha_reg__year=2024, estatus='assign'):
            for p2 in places[p.zona]['places']:
                if p2['uuid'] == str(p.uuid_place):
                    p2['folio_bd'] = p.folio
                    p2['date'] = p.fecha_reg
                    p2['section'] = places[p.zona]['title']
                    places_price = places_price + p2['price']
                    selected_places.append(p2)
        context['selected_places'] = selected_places
        context['places_price'] = places_price
        return context

class Shop(AdminPermissions, DetailView):
    template_name = 'admin/shop.html'
    model = Comercios
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def post(self, request, *args, **kwargs):
        shop_ = self.get_object()
        if 'validated' in request.POST:
            shop_.estatus = 'validated'
            shop_.save()
            Validaciones.objects.create(comercio=shop_, estatus='validated', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'rejected' in request.POST:
            shop_.estatus = 'rejected'
            shop_.save()
            Validaciones.objects.create(comercio=shop_, estatus='rejected', validador=request.user.get_full_name())
            messages.success(request, 'Estatus asignado exitosamente.')
        elif 'pending' in request.POST:
            validation_fields = ['nombre', 'descripcion', 'imagen', 'vende_alcohol', 'voltaje', 'equipos']
            data = {
                'just_fields': [],
                'field_comments': {}
            }
            for f in request.POST:
                if f in validation_fields:
                    if not request.POST.get(f).strip() == '':
                        data['just_fields'].append(f)
                        data['field_comments'][f] = request.POST.get(f).strip()
            if data['just_fields']:
                shop_.estatus = 'pending'
                shop_.save()
                Validaciones.objects.create(comercio=shop_, estatus='pending', validador=request.user.get_full_name(), campos=data)
                messages.success(request, 'Estatus asignado exitosamente.')
            else:
                messages.warning(request, 'No se realizó ninguna acción. No se detectaron campos validados.')
        return redirect('admin:shop', shop_.uuid)

class SetPlace(AdminPermissions, TemplateView):
    template_name = 'admin/set_place.html'

@api_view(['GET'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def render_place(request, key):
    places = {'n_1': nave1, 'n_3': nave3, 'z_a': zona_a}
    for p in places[key]['places']:
        if p['uuid']:
            p['status'] = 'available'
            if Lugares.objects.filter(uuid_place=p['uuid']).exists():
                p['status'] = 'unavailable'
    return Response(places[key])

@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def set_place_temp(request, uuid, zone):
    places = request.POST.getlist('places')
    request_ = Solicitudes.objects.get(uuid=uuid)
    objects = []
    if zone in ['z_a', 'z_b', 'z_c', 'z_d', 'n_1', 'n_3']:
        for p in places:
            objects.append(Lugares(uuid_place=p, solicitud=request_, usuario=request.user, estatus='temp', zona=zone))
        try:
            obj = Lugares.objects.bulk_create(objects)
            for o in obj:
                o.save()
            return Response({'status_code': 'saved'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'status_code': 'notsaved'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def unset_place_temp(request, uuid):
    places = request.POST.getlist('places')
    for p in places:
        p_ = Lugares.objects.filter(uuid_place=p, estatus='temp')
        if p_.exists():
            p_.get().delete()
    return Response({})

@api_view(['POST'])
@renderer_classes((JSONRenderer,))
@permission_classes([IsAuthenticated,])
def set_place(request, uuid):
    places = request.POST.getlist('places')
    for p in places:
        p_ = Lugares.objects.filter(uuid_place=p)
        if p_.exists():
            pl = p_.get()
            pl.estatus = 'assign'
            pl.save()
    return Response({})

class DownloadDateDoc(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            date = CitasAgendadas.objects.get(uuid=kwargs['uuid_date'])
            doc = get_date_constancy(request_, date)
            return doc
        except (Solicitudes.DoesNotExist, CitasAgendadas.DoesNotExist):
            raise Http404()

class UnlockRequest(AdminPermissions, RedirectView):
    def get(self, request, *args, **kwargs):
        try:
            request_ = Solicitudes.objects.get(uuid=kwargs['uuid'])
            validation = request_.get_last_unattended_validation()
            if validation:
                validation.atendido = True
                validation.save()
            request_.estatus = ''
            request_.save()
            Validaciones.objects.create(solicitud=request_, comentarios='Validación desbloqueada por el validador', estatus='pending', atendido=True, validador=request.user.get_full_name())
            messages.success(request, 'Validación Desbloqueada')
            return redirect('admin:request', request_.uuid)
        except (Solicitudes.DoesNotExist):
            raise Http404()