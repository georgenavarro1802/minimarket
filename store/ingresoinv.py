#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render_to_response

from store.forms import IngresoProductoForm, DetalleIngresoProductoForm, ProveedorForm
from store.functions import ok_json, bad_json, salva_auditoria
from store.models import Proveedor, IngresoProducto, Producto, DetalleIngresoProducto, InventarioReal
from store.values import ACCION_ADICIONAR
from store.views import addUserData


@login_required(redirect_field_name='ret', login_url='/login')
def view(request):
    data = {'title': 'Purchase'}
    addUserData(request, data)
    if request.method == 'POST':
        action = request.POST['action']
        if action == 'ingresoinv':
            try:
                with transaction.atomic():
                    datos = json.loads(request.POST['datos'])
                    ingresoprod = IngresoProducto(proveedor_id=datos['proveedor'],
                                                  numerodocumento=datos['numerodocumento'],
                                                  descripcion=datos['descripcion'])
                    ingresoprod.save()

                    salva_auditoria(request, ingresoprod, ACCION_ADICIONAR)
                    # Items
                    items = datos['items']
                    for d in items:
                        codigo = d['codigo']
                        if Producto.objects.filter(codigo=codigo).exists():
                            producto = Producto.objects.filter(codigo=codigo)[0]
                            detalleingprod = DetalleIngresoProducto(purchase=ingresoprod,
                                                                    producto=producto,
                                                                    cantidad=Decimal(d['cantidad']),
                                                                    costo=Decimal(d['costo']),
                                                                    valor=Decimal(d['valor']))
                            detalleingprod.save()
                            salva_auditoria(request, detalleingprod, ACCION_ADICIONAR)

                            # Actualizar Inventario Real
                            if InventarioReal.objects.filter(producto=producto).exists():
                                inventarioreal = InventarioReal.objects.filter(producto=producto)[0]
                                inventarioreal.cantidad = inventarioreal.cantidad + detalleingprod.cantidad
                                inventarioreal.valor = inventarioreal.valor + detalleingprod.valor
                                inventarioreal.costo = inventarioreal.valor / inventarioreal.cantidad
                                inventarioreal.save()
                            else:
                                inventarioreal = InventarioReal(producto=detalleingprod.producto,
                                                                cantidad=detalleingprod.cantidad,
                                                                costo=detalleingprod.costo,
                                                                valor=detalleingprod.valor)
                                inventarioreal.save()
                            salva_auditoria(request, inventarioreal, ACCION_ADICIONAR)

                    return ok_json({'numero_purchase': ingresoprod.repr_id()})

            except Exception:
                return bad_json(error=1)

        elif action == 'chequeacodigos':
            codigos = request.POST['codigos'].split(",")
            if Producto.objects.filter(codigo__in=codigos).exists():
                cod_existen = [x.codigo for x in Producto.objects.filter(codigo__in=codigos)]
                return ok_json({"codigosexisten": cod_existen})
            else:
                return bad_json(error=1)

        elif action == 'comprobarnumero':
            proveedor = Proveedor.objects.get(pk=request.POST['pid'])
            numero = request.POST['numero']
            if IngresoProducto.objects.filter(numerodocumento=numero, proveedor=proveedor).exists():
                return bad_json(error=1)
            else:
                return ok_json()

    else:
        data['fechahoy'] = datetime.today()
        data['form'] = IngresoProductoForm(initial={'fechadocumento': data['fechahoy']})
        data['form4'] = DetalleIngresoProductoForm()
        data['form_entidad'] = ProveedorForm(prefix='proveedor')
        return render_to_response("ingresoinv/ingresoinv.html", data)
