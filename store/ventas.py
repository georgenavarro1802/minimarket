#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response

from store.forms import ClienteForm
from store.functions import salva_auditoria, url_back, mensaje_excepcion
from store.models import (TipoProducto, InventarioReal, Venta, Cliente, DetalleVenta, Producto, SesionCaja)
from store.values import TIPO_PRODUCTOS_FAVORITOS_ID, ACCION_ADICIONAR
from store.views import addUserData


def convertir_cadena_hora(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f").time()


def convertir_hora_cadena(h):
    return h.strftime("%Y-%m-%dT%H:%M:%S.%f")


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    ex = None
    data = {'title': 'Sales'}
    addUserData(request, data)
    try:
        sesioncaja = SesionCaja.objects.filter(abierta=True)[0]
    except:
        return HttpResponseRedirect('/?info=Open a Cash Register Session to enter to this module')

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'guardar':
            try:
                with transaction.atomic():
                    datos = json.loads(request.POST['items'])
                    productos = json.loads(request.POST['productos'])

                    venta = Venta(sesioncaja=sesioncaja,
                                  cliente_id=int(datos['clienteid']),
                                  numero=sesioncaja.facturatermina,
                                  subtotal=Decimal(datos['subtotal']),
                                  iva=Decimal(datos['iva']),
                                  total=Decimal(datos['total']),
                                  pago=Decimal(datos['pago']),
                                  devolucion=Decimal(datos['devolucion']))
                    venta.save()
                    for pr in productos:
                        producto = Producto.objects.get(codigo=pr['codproducto'])
                        dv = DetalleVenta(venta=venta,
                                          producto=producto,
                                          cantidad=Decimal(pr['cantidad']),
                                          pvp=Decimal(pr['pvpproducto']),
                                          valor=Decimal(pr['valor']),
                                          iva=Decimal(pr['iva']),
                                          subtotal=Decimal(pr['subtotal']))
                        dv.save()

                        # Actualizar Inventario
                        if InventarioReal.objects.filter(producto=producto).exists():
                            ir = InventarioReal.objects.filter(producto=producto)[0]
                            ir.cantidad -= dv.cantidad
                            ir.valor = (ir.cantidad * ir.costo).quantize(Decimal(10) ** -2)
                            ir.costo = Decimal(ir.valor / ir.cantidad).quantize(Decimal(10)**-2) if ir.cantidad else Decimal(0)
                            ir.save()

                    sesioncaja.facturatermina += 1
                    sesioncaja.save()

                    salva_auditoria(request, venta, ACCION_ADICIONAR)

                    return HttpResponse(json.dumps({"result": "ok",
                                                    "urlimpresion": '/ventas?action=impresion&idventa=' + str(venta.id)}),
                                        content_type="application/json")

            except Exception as ex:
                return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")

        elif action == 'datoscliente':
            if Cliente.objects.filter(ruc=request.POST['ruccliente']).exists():
                cliente = Cliente.objects.filter(ruc=request.POST['ruccliente'])[0]
                return HttpResponse(json.dumps({"result": "ok",
                                                "ruc": cliente.ruc,
                                                "nombre": cliente.nombre,
                                                "telefono": cliente.telefono,
                                                "direccion": cliente.direccion}),
                                    content_type="application/json")
            else:
                return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")

        return HttpResponseRedirect("/ventas")

    else:
        if 'action' in request.GET:
            action = request.GET['action']
            if action == 'buscaproductos':
                try:
                    data['tipoprod'] = tipoprod = TipoProducto.objects.get(pk=request.GET['tipoid'])
                    if tipoprod.id == TIPO_PRODUCTOS_FAVORITOS_ID:
                        inventarios = InventarioReal.objects.filter(producto__esfavorito=True)
                    else:
                        inventarios = InventarioReal.objects.filter(producto__tipoproducto=tipoprod)

                    data['productos_existencias'] = inventarios
                    data['clientes'] = Cliente.objects.all()
                    return render_to_response("ventas/buscaproductos.html", data)
                except Exception as ex:
                    pass

            elif action == 'buscaproducto':
                try:
                    producto = Producto.objects.get(pk=request.GET['pid'])
                    data['producto_existencia'] = producto.inventarioreal_set.all()
                    return render_to_response("ventas/productobuscado.html", data)
                except Exception as ex:
                    pass

            elif action == 'impresion':
                venta = Venta.objects.get(pk=request.GET['idventa'])
                try:
                    datos_generales_impresion = []
                    datos_productos_impresion = []
                    datos_generales_impresion.append((venta.cliente.ruc,
                                                      venta.cliente.nombre,
                                                      venta.cliente.direccion,
                                                      venta.subtotal,
                                                      venta.iva,
                                                      venta.total,
                                                      venta.pago,
                                                      venta.devolucion,
                                                      venta.cliente.telefono,
                                                      venta.fecha.strftime('%d-%m-%Y')))

                    # Lista de Productos a recorrer
                    for det in venta.detalleventa_set.all():
                        datos_productos_impresion.append((det.producto.alias,
                                                          det.cantidad,
                                                          det.pvp,
                                                          det.valor))

                    data['datos_productos_impresion'] = datos_productos_impresion
                    data['datos_generales_impresion'] = datos_generales_impresion
                    return render_to_response("ventas/impresion.html", data)
                except Exception as ex:
                    pass

            return HttpResponseRedirect(url_back(request, mensaje_excepcion(ex.args[0])))

        data['hoy'] = datetime.today()
        data['tipos_productos'] = TipoProducto.objects.all()
        data['form'] = ClienteForm()
        tipo_prod1 = TipoProducto.objects.all().order_by('id')[0]
        data['productos'] = InventarioReal.objects.filter(producto__tipoproducto=tipo_prod1)
        data['lista_productos'] = Producto.objects.filter(activo=True)
        return render_to_response("ventas/productos.html", data)
