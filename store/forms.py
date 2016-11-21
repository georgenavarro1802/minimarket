#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from decimal import Decimal
from django import forms
from store.models import TipoProducto


class ExtFileField(forms.FileField):
    """
    * max_upload_size - a number indicating the maximum file size allowed for upload.
            500Kb - 524288
            1MB - 1048576
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB 104857600
            250MB - 214958080
            500MB - 429916160
    t = ExtFileField(ext_whitelist=(".pdf", ".txt"), max_upload_size=)
    """

    def __init__(self, *args, **kwargs):
        ext_whitelist = kwargs.pop("ext_whitelist")
        self.ext_whitelist = [i.lower() for i in ext_whitelist]
        self.max_upload_size = kwargs.pop("max_upload_size")
        super(ExtFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        upload = super(ExtFileField, self).clean(*args, **kwargs)
        if upload:
            size = upload.size
            filename = upload.name
            ext = os.path.splitext(filename)[1]
            ext = ext.lower()

            if size == 0 or ext not in self.ext_whitelist or size > self.max_upload_size:
                raise forms.ValidationError("Tipo de fichero o tamanno no permitido!")


class ProductoForm(forms.Form):
    tipoproducto = forms.ModelChoiceField(TipoProducto.objects, label=u'Category',
                                          widget=forms.Select(attrs={'class': 'imp-50'}))
    codigo = forms.CharField(label=u'Code', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    codigobarra = forms.CharField(max_length=20, label=u'Barcode', required=False,
                                  widget=forms.TextInput(attrs={'class': 'imp-25'}))
    descripcion = forms.CharField(max_length=50, label=u'Description', widget=forms.TextInput())
    unidadmedida = forms.CharField(max_length=3, label=u'UM', initial='UNO',
                                   widget=forms.TextInput(attrs={'class': 'imp-10'}))
    alias = forms.CharField(max_length=20, label=u'Alias',
                            widget=forms.TextInput(attrs={'class': 'imp-25'}))
    pvp = forms.DecimalField(max_digits=11, decimal_places=2, label=u'Price',
                             widget=forms.TextInput(attrs={'class': 'imp-25'}))
    esfavorito = forms.BooleanField(label=u'Favorite?', required=False)

    def for_addproducto(self):
        self.fields['codigo'].widget.attrs['readonly'] = True

    def for_editproducto(self):
        self.fields['codigo'].widget.attrs['readonly'] = True
        self.fields['tipoproducto'].widget.attrs['readonly'] = True


class ProveedorForm(forms.Form):
    identificacion = forms.CharField(max_length=50, label=u'Identification',
                                     widget=forms.TextInput(attrs={'class': 'imp-25'}))
    nombre = forms.CharField(max_length=200, label=u'Name', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    alias = forms.CharField(max_length=100, label=u'Alias', required=False,
                            widget=forms.TextInput(attrs={'class': 'imp-25'}))
    direccion = forms.CharField(max_length=200, label=u'Address', widget=forms.TextInput())
    telefono = forms.CharField(max_length=100, label=u'Phone', widget=forms.TextInput(attrs={'class': 'imp-50'}))
    celular = forms.CharField(max_length=100, label=u'Mobile', widget=forms.TextInput(attrs={'class': 'imp-50'}))
    email = forms.CharField(max_length=200, label=u'Email', widget=forms.TextInput(attrs={'class': 'imp-75'}))


class IngresoProductoForm(forms.Form):
    proveedor = forms.CharField(label=u'Supplier', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    descripcion = forms.CharField(label=u'Description', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    numerodocumento = forms.CharField(label=u'Document No.', widget=forms.TextInput(attrs={'class': 'imp-50'}))


class DetalleIngresoProductoForm(forms.Form):
    codigoprod = forms.CharField(max_length=10, label=u'Code', widget=forms.TextInput(attrs={'class': 'imp-50'}))
    tipoprod = forms.ModelChoiceField(TipoProducto.objects, label=u"Category",
                                      widget=forms.Select(attrs={'class': 'imp-75'}))
    descripcionprod = forms.CharField(label=u'Description', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    unidadmedidaprod = forms.CharField(max_length=3, label=u'Unit Measur.',
                                       widget=forms.TextInput(attrs={'class': 'imp-10'}))
    cantidadprod = forms.DecimalField(max_digits=11, decimal_places=2, label=u'Cantidad', initial=Decimal('0'),
                                      widget=forms.TextInput(attrs={'class': 'imp-25'}))
    costoprod = forms.DecimalField(max_digits=11, decimal_places=2, label='Costo', initial=Decimal('0.00'),
                                   widget=forms.TextInput(attrs={'class': 'imp-25'}))
    valorprod = forms.DecimalField(max_digits=11, decimal_places=2, label='Valor', initial=Decimal('0.00'),
                                   widget=forms.TextInput(attrs={'class': 'imp-25'}))


class ClienteForm(forms.Form):
    ruc = forms.CharField(max_length=20, label=u'Identification', widget=forms.TextInput(attrs={'class': 'imp-25'}))
    nombre = forms.CharField(max_length=200, label=u'Name', widget=forms.TextInput())
    direccion = forms.CharField(max_length=200, label=u'Address', widget=forms.TextInput())
    email = forms.CharField(max_length=100, label=u'Email', widget=forms.TextInput(attrs={'class': 'imp-75'}))
    telefono = forms.CharField(max_length=100, label=u'Phone', widget=forms.TextInput(attrs={'class': 'imp-50'}))


class FotoProductoForm(forms.Form):
    foto = ExtFileField(label='Seleccione Imagen',
                        help_text='Tamano Maximo permitido 2 mb, en formato jpeg, jpg, gif, png, bmp',
                        ext_whitelist=(".jpeg", ".jpg", ".gif", ".png", ".bmp"), max_upload_size=2097152)


class SesionCajaForm(forms.Form):
    fondo = forms.FloatField(label=u"Initial Cash Fund", widget=forms.TextInput(attrs={'class': 'imp-50'}))
    facturaempieza = forms.IntegerField(label=u"Initial Invoice No.", widget=forms.TextInput(attrs={'class': 'imp-50'}))
    cajero = forms.CharField(label=u"Cashier", widget=forms.TextInput())


class CierreSesionCajaForm(forms.Form):
    bill100 = forms.IntegerField(initial=0, label="Bills of 100", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bill50 = forms.IntegerField(initial=0, label="Bills of 50", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bill20 = forms.IntegerField(initial=0, label="Bills of 20", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bill10 = forms.IntegerField(initial=0, label="Bills of 10", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bill5 = forms.IntegerField(initial=0, label="Bills of 5", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bill2 = forms.IntegerField(initial=0, label="Bills of 2", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    bill1 = forms.IntegerField(initial=0, label="Bills of 1", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    enmonedas = forms.FloatField(initial=0, label="Coins Value", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    deposito = forms.FloatField(initial=0, label="Deposits", widget=forms.TextInput(attrs={'class': 'imp-25'}))
    total = forms.FloatField(initial=0, label="Total", required=False, widget=forms.TextInput(attrs={'class': 'imp-25'}))


class AnularVentaForm(forms.Form):
    motivo = forms.CharField(max_length=200, label='Motivo')


class CambioClaveForm(forms.Form):
    anterior = forms.CharField(label='Current Password', widget=forms.PasswordInput)
    nueva = forms.CharField(label='New Password', widget=forms.PasswordInput)
    repetir = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)
