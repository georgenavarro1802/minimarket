# ! /usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.db.models.aggregates import Sum


class ModuloGrupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200, blank=True)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return "{0}".format(self.nombre)

    class Meta:
        verbose_name = 'Modules Group'
        verbose_name_plural = "Modules Groups"
        db_table = 'modules_groups'
        ordering = ('orden', 'nombre')

    def modulos_activos(self):
        return self.modulo_set.filter(activo=True)


class Modulo(models.Model):
    grupo = models.ForeignKey(ModuloGrupo)
    url = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=200)
    orden = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return "{0} (/{1})".format(self.nombre, self.url)

    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        db_table = 'modules'
        ordering = ('grupo', 'orden')


class Proveedor(models.Model):
    nombre = models.CharField(max_length=300)
    alias = models.CharField(max_length=100, blank=True, null=True)
    identificacion = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=100, blank=True, null=True)
    celular = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.nombre)

    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        db_table = 'suppliers'
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Proveedor.objects.filter(Q(nombre__contains=q) | Q(alias__contains=q) | Q(identificacion__contains=q))

    def flexbox_repr(self):
        return "%s - %s" % (self.identificacion, self.nombre)

    def flexbox_alias(self):
        return self.nombre

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.nombre = self.nombre.upper()
        self.alias = self.alias.upper()
        self.identificacion = self.identificacion.upper()
        self.direccion = self.direccion.upper()
        if self.telefono:
            self.telefono = self.telefono.upper()
        if self.celular:
            self.celular = self.celular.upper()
        if self.email:
            self.email = self.email.lower()
        super(Proveedor, self).save(force_insert, force_update, using)


class TipoProducto(models.Model):
    nombre = models.CharField(max_length=100)
    inicial = models.IntegerField(default=0)

    def __str__(self):
        return "{0} - {1}".format(self.inicial, self.nombre)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'
        db_table = 'categories'
        ordering = ('inicial', )

    def tiene_producto_asociado(self):
        return self.producto_set.exists()

    @staticmethod
    def flexbox_query(q):
        return TipoProducto.objects.filter(Q(nombre__contains=q) | Q(inicial__contains=q))

    def flexbox_repr(self):
        return "%s - %s " % (self.inicial, self.nombre)

    def flexbox_alias(self):
        return [self.inicial, self.nombre]

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        if self.nombre:
            self.nombre = self.nombre.upper()
        super(TipoProducto, self).save(force_insert, force_update, using)


class Producto(models.Model):
    codigo = models.CharField(max_length=10)
    codigobarra = models.CharField(max_length=20, blank=True, null=True)
    descripcion = models.CharField(max_length=50)
    unidadmedida = models.CharField(max_length=3, default="UNO")
    tipoproducto = models.ForeignKey(TipoProducto)
    alias = models.CharField(max_length=20)
    pvp = models.DecimalField(max_digits=11, decimal_places=2)
    activo = models.BooleanField(default=True)
    esfavorito = models.BooleanField(default=False)
    foto = models.FileField(upload_to='fotoaf/%Y/%m/%d')

    def __str__(self):
        return '%s - %s (%s) [%s]' % (self.codigo, self.descripcion, unicode(self.unidadmedida), str(self.pvp))

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        db_table = 'products'
        ordering = ('codigo', )

    def nombre_corto(self):
        return "{0} - {1}".format(self.codigo, self.descripcion)

    def download_foto(self):
        return self.foto.url

    @staticmethod
    def flexbox_query(q):
        return Producto.objects.filter(Q(codigo__contains=q) | Q(descripcion__contains=q) | Q(alias__contains=q))

    def flexbox_repr(self):
        return "%s - %s (%s)" % (self.codigo, self.descripcion, self.unidadmedida)

    def flexbox_alias(self):
        return [self.codigo, self.descripcion, self.unidadmedida, self.tipoproducto.id]

    def inventario(self):
        return self.inventarioreal_set.filter(cantidad__gt=0)[0] if self.inventarioreal_set.exists() else None


class IngresoProducto(models.Model):
    proveedor = models.ForeignKey(Proveedor)
    numerodocumento = models.CharField(max_length=20, blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return "{0} {1} - {2}".format(self.proveedor.nombre, self.numerodocumento, self.fecha.strftime('%d-%m-%Y'))

    class Meta:
        verbose_name = 'Purchase'
        verbose_name_plural = 'Purchases'
        db_table = 'purchases'
        ordering = ('fecha', )

    def total_ingreso(self):
        return self.detalleingresoproducto_set.all().aggregate(Sum('valor'))['valor__sum']

    def repr_id(self):
        return str(self.id).zfill(6)


class DetalleIngresoProducto(models.Model):
    purchase = models.ForeignKey(IngresoProducto)
    producto = models.ForeignKey(Producto)
    cantidad = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    costo = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    valor = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)

    def __str__(self):
        return "{0} - Cant: {1}, Cost: ${2}".format(self.producto.codigo, self.cantidad, self.costo)

    class Meta:
        verbose_name = 'Purchase Detail'
        verbose_name_plural = 'Purchase Details'
        db_table = 'purchase_details'
        ordering = ('purchase', 'producto')


class InventarioReal(models.Model):
    producto = models.ForeignKey(Producto)
    cantidad = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    costo = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    valor = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)

    def __str__(self):
        return "{0} - Cant: {1}, Cost: ${2}".format(self.producto.codigo, self.cantidad, self.costo)

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'
        db_table = 'inventories'
        ordering = ('producto',)


class Cliente(models.Model):
    ruc = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "{0} - {1}".format(self.ruc, self.nombre)

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        db_table = 'customers'
        ordering = ('nombre', )

    @staticmethod
    def flexbox_query(q):
        return Cliente.objects.filter(Q(nombre__contains=q) | Q(ruc__contains=q))

    def flexbox_repr(self):
        return unicode(self)

    def flexbox_alias(self):
        return [self.ruc, self.nombre, self.direccion, self.telefono]


class SesionCaja(models.Model):
    fecha = models.DateTimeField()
    fondo = models.DecimalField(max_digits=11, decimal_places=2)
    facturaempieza = models.IntegerField(default=0)
    facturatermina = models.IntegerField(default=0)
    abierta = models.BooleanField(default=True)
    cajero = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "{0} - {1} a {2}".format(self.fecha.strftime("%d-%m-%Y"), self.facturaempieza, self.facturatermina)

    class Meta:
        verbose_name = "Cash Register Session"
        verbose_name_plural = "Cash Register Sessions"
        db_table = 'cashregisters_sessions'
        ordering = ('-fecha', )

    def repr_id(self):
        return str(self.id).zfill(6)

    @staticmethod
    def flexbox_query(q):
        if len(q) == 10 and q[2] == '-' and q[2] == '-':
            try:
                fecha = datetime(int(q[6:10]), int(q[3:5]), int(q[0:2])).date()
                return SesionCaja.objects.filter(fecha=fecha)
            except:
                pass

        return SesionCaja.objects.filter(Q(fecha__icontains=q) | Q(cajero__icontains=q))

    def flexbox_repr(self):
        return self.caja.nombre + " [" + self.fecha.strftime("%d-%m-%Y") + ", " + self.hora.strftime("%H:%M") + "]"

    def flexbox_alias(self):
        return self.caja.nombre + " " + self.fecha.strftime("%d-%m-%Y")

    def hora_cierre(self):
        return self.cierresesioncaja_set.all()[0].fecha.time if self.cierresesioncaja_set.exists() else ""

    def cierre_sesion(self):
        try:
            return self.cierresesioncaja_set.all()[0]
        except:
            return None

    def total_efectivo_sesion(self):
        valor = self.venta_set.filter(valida=True).aggregate(suma=Sum('total'))['suma']
        return Decimal(valor) if valor else 0

    def total_sesion(self):
        return self.total_efectivo_sesion()


class CierreSesionCaja(models.Model):
    sesion = models.ForeignKey(SesionCaja)
    total = models.FloatField(default=0)
    bill100 = models.IntegerField(null=True, blank=True, default=0)
    bill50 = models.IntegerField(null=True, blank=True, default=0)
    bill20 = models.IntegerField(null=True, blank=True, default=0)
    bill10 = models.IntegerField(null=True, blank=True, default=0)
    bill5 = models.IntegerField(null=True, blank=True, default=0)
    bill2 = models.IntegerField(null=True, blank=True, default=0)
    bill1 = models.IntegerField(null=True, blank=True, default=0)
    enmonedas = models.FloatField(null=True, blank=True, default=0)
    deposito = models.FloatField(null=True, blank=True, default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cash Register Close Sessions: ".format(self.sesion.repr_id())

    class Meta:
        verbose_name = "Cash Register Closed Session"
        verbose_name_plural = "Cash Register Closed Sessions"
        db_table = 'cashregisters_closesessions'
        ordering = ('sesion', )

    def calcula_total(self):
        return self.bill100 * 100 + self.bill50 * 50 + self.bill20 * 20 + self.bill10 * 10 + \
               self.bill5 * 5 + self.bill2 * 2 + self.bill1 * 1 + self.enmonedas + self.deposito

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.total = self.calcula_total()
        super(CierreSesionCaja, self).save(force_insert=force_insert, force_update=force_update, using=using)


class Venta(models.Model):
    sesioncaja = models.ForeignKey(SesionCaja)
    cliente = models.ForeignKey(Cliente)
    numero = models.CharField(max_length=20)
    fecha = models.DateField(auto_now_add=True)
    subtotal = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    iva = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    total = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    pago = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    devolucion = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    valida = models.BooleanField(default=True)
    motivoanulacion = models.CharField(max_length=200, blank=True, null=True)
    usuarioanula = models.ForeignKey(User, blank=True, null=True)

    def __str__(self):
        return "{0} {1} {2}".format(self.numero, self.cliente.nombre, self.total)

    class Meta:
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'
        db_table = 'sales'
        ordering = ('fecha', )

    def cantidad_productos(self):
        return self.detalleventa_set.count()


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta)
    producto = models.ForeignKey(Producto)
    cantidad = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    pvp = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    valor = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    iva = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)
    subtotal = models.DecimalField(default=Decimal('0.00'), max_digits=11, decimal_places=2)

    def __str__(self):
        return "{0} {1}".format(self.venta.numero, self.producto.codigo)

    class Meta:
        verbose_name = 'Sale Detail'
        verbose_name_plural = 'Sales Details'
        db_table = 'sales_details'
        ordering = ('venta', )
