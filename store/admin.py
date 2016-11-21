#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib import admin

from store.models import (TipoProducto, Proveedor, Producto, DetalleIngresoProducto, IngresoProducto, ModuloGrupo,
                          Modulo, InventarioReal, Cliente, SesionCaja, CierreSesionCaja, Venta, DetalleVenta)


class ModuloGrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'orden', 'activo')
    search_fields = ('nombre', 'descripcion')
    list_filter = ('activo', )

admin.site.register(ModuloGrupo, ModuloGrupoAdmin)


class ModuloAdmin(admin.ModelAdmin):
    list_display = ('url', 'grupo', 'nombre', 'icono', 'descripcion', 'icono', 'orden', 'activo')
    search_fields = ('url', 'nombre', 'descripcion', 'grupo__nombre')
    list_filter = ('activo', )

admin.site.register(Modulo, ModuloAdmin)


class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'alias', 'identificacion', 'direccion', 'telefono', 'celular', 'email')
    search_fields = ('nombre', 'identificacion')

admin.site.register(Proveedor, ProveedorAdmin)


class TipoProductoAdmin(admin.ModelAdmin):
    list_display = ('inicial', 'nombre')
    search_fields = ('nombre',)
    list_filter = ('inicial', )

admin.site.register(TipoProducto, TipoProductoAdmin)


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'codigobarra', 'descripcion', 'unidadmedida', 'tipoproducto', 'alias',
                    'pvp', 'activo', 'esfavorito', 'foto')
    search_fields = ('codigo', 'codigobarra', 'descripcion', 'tipoproducto__nombre', 'alias')
    list_filter = ('activo', 'esfavorito')

admin.site.register(Producto, ProductoAdmin)


class IngresoProductoAdmin(admin.ModelAdmin):
    list_display = ('proveedor', 'numerodocumento', 'fecha', 'descripcion')
    search_fields = ('proveedor__nombre', 'fecha', 'descripcion')
    list_filter = ('proveedor', )

admin.site.register(IngresoProducto, IngresoProductoAdmin)


class DetalleIngresoProductoAdmin(admin.ModelAdmin):
    list_display = ('purchase', 'producto', 'cantidad', 'costo', 'valor')
    search_fields = ('producto__nombre', 'producto__descripcion')

admin.site.register(DetalleIngresoProducto, DetalleIngresoProductoAdmin)


class InventarioRealAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad', 'costo', 'valor')
    search_fields = ('producto__nombre', 'producto__descripcion')

admin.site.register(InventarioReal, InventarioRealAdmin)


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('ruc', 'nombre', 'direccion', 'telefono')
    search_fields = ('ruc', 'nombre')

admin.site.register(Cliente, ClienteAdmin)


class SesionCajaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'fondo', 'facturaempieza', 'facturatermina', 'abierta', 'cajero')
    list_filter = ('abierta', )

admin.site.register(SesionCaja, SesionCajaAdmin)


class CierreSesionCajaAdmin(admin.ModelAdmin):
    list_display = ('sesion', 'total', 'bill100', 'bill50', 'bill20', 'bill10', 'bill5', 'bill2', 'bill1',
                    'enmonedas', 'deposito', 'fecha')
    search_fields = ('sesion',)

admin.site.register(CierreSesionCaja, CierreSesionCajaAdmin)


class VentaAdmin(admin.ModelAdmin):
    list_display = ('sesioncaja', 'cliente', 'numero', 'fecha', 'subtotal', 'iva', 'total',
                    'pago', 'devolucion', 'valida')
    search_fields = ('cliente__nombre', 'numero')
    list_filter = ('valida', )

admin.site.register(Venta, VentaAdmin)


class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'pvp', 'valor', 'iva', 'subtotal')
    search_fields = ('venta__numero', 'producto__descripcion', 'producto__codigo')

admin.site.register(DetalleVenta, DetalleVentaAdmin)
