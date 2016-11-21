# #! /usr/bin/env python
# # -*- coding: utf-8 -*-
#
# import json
# from datetime import datetime
# from decimal import Decimal
#
# from django.contrib.admin.models import LogEntry, DELETION
# from django.contrib.auth.decorators import login_required
# from django.contrib.contenttypes.models import ContentType
# from django.core.paginator import Paginator
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import render_to_response
# from django.utils.encoding import force_unicode
#
# from store.forms import AnularVentaForm
# from store.models import (Venta, InventarioReal, DetalleIngresoProducto, Cliente, SesionCaja)
# from store.views import addUserData, salva_auditoria
# from values import CLIENTES_EXTERNOS_ID, ACCION_MODIFICAR
#
#
# @login_required(redirect_field_name='ret', login_url='/login')
# def view(request):
#     if request.method == 'POST':
#         action = request.POST['action']
#         if action == 'anularff':
#             venta = Venta.objects.get(pk=request.POST['id'])
#             f = AnularVentaForm(request.POST)
#             if f.is_valid():
#                 venta.valida = False
#                 venta.usuarioanula = request.user
#                 venta.motivoanulacion = f.cleaned_data['motivo']
#                 venta.save()
#
#                 salva_auditoria(request, venta, ACCION_MODIFICAR)
#
#                 # Actualizar Inventario
#                 for d in venta.detalles.all():
#                     if InventarioReal.objects.filter(producto=d.producto).exists():
#                         inventarioreal = InventarioReal.objects.filter(producto=d.producto)[0]
#                         inventarioreal.cantidad = inventarioreal.cantidad + d.cantidad
#                         ultimoingresoprod = None
#                         if DetalleIngresoProducto.objects.filter(producto=d.producto).exists():
#                             ultimoingresoprod = DetalleIngresoProducto.objects.filter(producto=d.producto).latest('id')
#                         if ultimoingresoprod:
#                             inventarioreal.valor = inventarioreal.valor + ultimoingresoprod.valor
#                             inventarioreal.costo = inventarioreal.valor / inventarioreal.cantidad
#                             inventarioreal.save()
#                         else:
#                             inventarioreal.valor = inventarioreal.valor + d.valor
#                             inventarioreal.costo = inventarioreal.valor / inventarioreal.cantidad
#                             inventarioreal.save()
#
#                     else:
#                         inventarioreal = InventarioReal(producto=d.producto,
#                                                         cantidad=d.cantidad,
#                                                         costo=d.pvp,
#                                                         valor=d.valor)
#                         inventarioreal.save()
#
#                 return HttpResponseRedirect('/cons_ventas')
#
#             else:
#
#                 return HttpResponseRedirect('/cons_ventas?action=anular&id=' + str(venta.id))
#
#         elif action == 'add':
#             try:
#                 datos = json.loads(request.POST['datos'])
#                 sesioncaja = SesionCaja.objects.get()
#                 if not Cliente.objects.filter(ruc=datos['ruc']).exists():
#                     cliente = Cliente(ruc=datos['ruc'],
#                                       nombre=datos['nombre'],
#                                       direccion=datos['direccion'],
#                                       telefono=datos['telefono'])
#                     cliente.save()
#                 else:
#                     cliente = Cliente.objects.filter(ruc=datos['ruc'])[0]
#
#                 venta = Venta(numero=sesioncaja.facturatermina,
#                               fecha=datetime.now(),
#                               valida=True, cliente=cliente,
#                               subtotal=datos['sub'], total=datos['total'],
#                               sesioncaja=sesioncaja, iva=datos['iva'])
#                 venta.save()
#
#                 salva_auditoria(request, venta, )
#                         try:
#                             # case server externo
#                             client_address = request.META['HTTP_X_FORWARDED_FOR']
#                         except:
#                             # case localhost o 127.0.0.1
#                             client_address = request.META['REMOTE_ADDR']
#
#                             # Log de ADICIONAR FACTURA
#                             LogEntry.objects.log_action(
#                                 user_id=request.user.pk,
#                                 content_type_id=ContentType.objects.get_for_model(factura).pk,
#                                 object_id=cliente.id,
#                                 object_repr=force_unicode(factura),
#                                 action_flag=DELETION,
#                                 change_message='Adicionada Factura (' + client_address + ')')
#
#                             usuariotrans = UsuarioTransaccion(transaccion=factura.id, usuario=usuario,
#                                                               tipotrans='Anulada Venta', ip=client_address)
#                             usuariotrans.save()
#
#                         sesioncaja.facturatermina = sesioncaja.facturatermina + 1
#                         sesioncaja.save()
#
#                         for dt in datos['items']:
#                             df = DetalleFactura(cantidad=int(dt['cantidad']),
#                                                 detalle=dt['detalle'],
#                                                 pvp=Decimal(dt['pvp']), iva=Decimal(dt['iva']),
#                                                 subtotal=Decimal(dt['subtotal']), total=Decimal(dt['total']))
#                             df.save()
#                             factura.detalle.add(df)
#                         return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")
#                     else:
#                         return HttpResponseRedirect("/?info=NO TIENE SESION DE CAJA ABIERTA")
#
#                 else:
#                     return HttpResponseRedirect("/?info=NO TIENE PERMISOS COMO CAJERO")
#
#             except Exception as ex:
#                 return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")
#
#         elif action == 'buscafactura':
#             usuario = request.user
#             if Caja.objects.filter(usuario=usuario).exists():
#                 caja = Caja.objects.filter(usuario=usuario)[:1].get()
#                 sesioncaja = caja.sesion_caja()
#                 if caja.sesion_caja():
#                     fact = sesioncaja.facturatermina
#                 return HttpResponse(json.dumps({"result": "ok", "factura": fact}), content_type="application/json")
#             else:
#                 return HttpResponse(json.dumps({"result": "bad"}), content_type="application/json")
#
#         elif action == 'anular':
#             factura = Factura.objects.get(pk=request.POST['id'])
#             f = AnularFacturaForm(request.POST)
#             usuario = request.user
#             if f.is_valid():
#                 factura.motivoanulacion = f.cleaned_data['motivo']
#                 factura.usuarioanula = usuario
#                 factura.valida = False
#                 factura.save()
#                 return HttpResponseRedirect('/facturas')
#             else:
#                 return HttpResponseRedirect('/facturas?action=anular&id=' + str(factura.id))
#
#
#
#     else:
#         data = {'title': 'Consulta de Facturas'}
#         addUserData(request, data)
#         if 'action' in request.GET:
#             action = request.GET['action']
#             if action == 'detallefact':
#                 data['factura'] = Factura.objects.get(pk=request.GET['idfactura'])
#                 return render_to_response('facturas/detallefacturas.html', data)
#
#             elif action == 'add':
#                 usuario = request.user
#                 if Caja.objects.filter(usuario=usuario).exists():
#                     caja = Caja.objects.filter(usuario=usuario)[:1].get()
#                     sesioncaja = caja.sesion_caja()
#                     if caja.sesion_caja():
#                         data['form'] = FacturaForm()
#                         data['form4'] = DetalleFacturaForm()
#                         data['CLIENTES_EXTERNOS_ID'] = CLIENTES_EXTERNOS_ID
#                         return render_to_response("facturas/add.html", data)
#                     else:
#                         return HttpResponseRedirect("/?info=NO TIENE SESION DE CAJA ABIERTA")
#                 else:
#                     return HttpResponseRedirect("/?info=NO TIENE PERMISOS COMO CAJERO")
#             elif action == 'impresion':
#                 cafeteria = request.session['cafeteria']
#                 cafeteria = Cafeteria.objects.get(pk=cafeteria.id)
#                 datos_generales_impresion = []
#                 datos_productos_impresion = []
#                 datos_generales_cafeteria = []
#                 factura = Factura.objects.get(pk=request.GET['idfact'])
#                 datos_generales_impresion.append(
#                     (factura.cliente.ruc, factura.cliente.nombre, factura.cliente.direccion, factura.cliente.telefono,
#                      factura.subtotal, factura.iva, factura.total, factura.fecha))
#
#                 # Lista de Productos a recorrer (salvar modelo Detalles Ventas)
#                 for det in factura.detalle.all():
#                     datos_productos_impresion.append((det.detalle, det.cantidad, det.pvp, det.total))
#
#                 datos_generales_cafeteria.append((cafeteria.nombre, cafeteria.direccion, cafeteria.ruc,
#                                                   cafeteria.telfijo, cafeteria.celular, cafeteria.logo))
#
#                 data['datos_productos_impresion'] = datos_productos_impresion
#                 data['datos_generales_impresion'] = datos_generales_impresion
#                 data['datos_generales_cafeteria'] = datos_generales_cafeteria
#                 return render_to_response("facturas/impresionfact.html", data)
#
#             elif action == 'anular':
#                 data['factura'] = Factura.objects.get(pk=request.GET['id'])
#                 data['form'] = AnularFacturaForm()
#                 return render_to_response('facturas/anulafactura.html', data)
#
#
#         else:
#             facturas = Factura.objects.filter(sesioncaja__caja__cafeteria=data['cafeteria']).order_by('-fecha',
#                                                                                                       '-numero')
#
#             paging = Paginator(facturas, 100)
#             p = 1
#             try:
#                 if 'page' in request.GET:
#                     p = int(request.GET['page'])
#                 page = paging.page(p)
#             except:
#                 page = paging.page(1)
#             data['paging'] = paging
#             data['page'] = page
#             data['facturas'] = page.object_list
#             return render_to_response("facturas/facturas.html", data)
