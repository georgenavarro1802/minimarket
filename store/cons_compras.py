#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.paginator import Paginator

from store.forms import AnularVentaForm
from store.models import DetalleIngresoProducto, IngresoProducto
from store.values import ACCION_MODIFICAR
from store.ventas import *
from store.views import addUserData


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
        data = {'title': 'Consulta de Compras'}
        addUserData(request, data)
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'detalle':
                data['compras'] = IngresoProducto.objects.get(pk=request.GET['idcompra'])
                return render_to_response('cons_compras/detallecompras.html', data)
            elif action == 'anular':
                data['venta'] = Venta.objects.get(pk=request.GET['id'])
                data['form'] = AnularVentaForm()
                return render_to_response('cons_ventas/anulaventa.html', data)
        else:
            compras = IngresoProducto.objects.all().order_by('-proveedor', '-fecha')
            paging = Paginator(compras, 25)
            p = 1
            try:
                if 'page' in request.GET:
                    p = int(request.GET['page'])
                page = paging.page(p)
            except:
                page = paging.page(1)
            data['paging'] = paging
            data['page'] = page
            data['compras'] = page.object_list
            return render_to_response("cons_compras/cons_compras.html", data)
