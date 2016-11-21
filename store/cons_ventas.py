#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.db.models import Sum

from store.forms import AnularVentaForm
from store.functions import MiPaginador
from store.models import DetalleIngresoProducto
from store.values import ACCION_MODIFICAR
from store.ventas import *


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'anular':
            venta = Venta.objects.get(pk=request.POST['id'])
            f = AnularVentaForm(request.POST)
            if f.is_valid():
                venta.valida = False
                venta.usuarioanula = request.user
                venta.motivoanulacion = f.cleaned_data['motivo']
                venta.save()

                salva_auditoria(request, venta, ACCION_MODIFICAR)

                # Actualizar Inventario
                for d in venta.detalles.all():
                    if InventarioReal.objects.filter(producto=d.producto).exists():
                        inventarioreal = InventarioReal.objects.filter(producto=d.producto)[0]
                        inventarioreal.cantidad = inventarioreal.cantidad + d.cantidad
                        ultimoingresoprod = None
                        if DetalleIngresoProducto.objects.filter(producto=d.producto).exists():
                            ultimoingresoprod = DetalleIngresoProducto.objects.filter(producto=d.producto).latest('id')
                        if ultimoingresoprod:
                            inventarioreal.valor = inventarioreal.valor + ultimoingresoprod.valor
                            inventarioreal.costo = inventarioreal.valor / inventarioreal.cantidad
                            inventarioreal.save()
                        else:
                            inventarioreal.valor = inventarioreal.valor + d.valor
                            inventarioreal.costo = inventarioreal.valor / inventarioreal.cantidad
                            inventarioreal.save()

                    else:
                        inventarioreal = InventarioReal(producto=d.producto,
                                                        cantidad=d.cantidad,
                                                        costo=d.pvp,
                                                        valor=d.valor)
                        inventarioreal.save()

                return HttpResponseRedirect('/cons_ventas')

            else:
                return HttpResponseRedirect('/cons_ventas?action=anular&id=' + str(venta.id))

    else:
        data = {'title': 'Consulta de Ventas'}
        addUserData(request, data)
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'detalle':
                data['venta'] = Venta.objects.get(pk=request.GET['idventa'])
                return render_to_response('cons_ventas/detalleventas.html', data)
            elif action == 'anular':
                data['venta'] = Venta.objects.get(pk=request.GET['id'])
                data['form'] = AnularVentaForm()
                return render_to_response('cons_ventas/anulaventa.html', data)
        else:
            search = None
            sesion = None

            if 'sesion' in request.GET:
                sesion = request.GET['sesion']
                data['sesionid'] = int(sesion) if sesion else ""
                data['sesion'] = SesionCaja.objects.get(pk=sesion) if sesion else ""
                data['totalventasesion'] = Venta.objects.filter(sesioncaja__id=sesion).aggregate(Sum('total'))['total__sum'] if sesion else ""
                data['cantidadventasesion'] = Venta.objects.filter(sesioncaja__id=sesion).count() if sesion else ""
                data['creditosesion'] = pagos_total_fecha_credito_sesion(data['sesion']) if sesion else ""
                data['valessesion'] = ""
                data['depositarsesion'] = data['totalventasesion'] - data['creditosesion'] - data['valessesion'] if sesion else ""
                data['promedioventasesion'] = Decimal(data['totalventasesion'] / data['cantidadventasesion']).quantize(Decimal(10) ** -2) if sesion else ""

            if 's' in request.GET:
                search = request.GET['s']

            if search:
                ventas = Venta.objects.filter(id__icontains=search)
            elif sesion:
                ventas = Venta.objects.filter(sesioncaja__id=sesion).order_by('-fecha', '-id', '-hora')
            else:
                ventas = Venta.objects.all()

            paging = MiPaginador(ventas, 25)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(1)

            data['paging'] = paging
            data['rangospaging'] = paging.rangos_paginado(p)
            data['page'] = page
            data['search'] = search if search else ""
            data['ventas'] = page.object_list
            data['sesionescaja'] = SesionCaja.objects.all().order_by('fecha')
            return render_to_response("cons_ventas/cons_ventas.html", data)
