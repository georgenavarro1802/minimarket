# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-21 01:52
from __future__ import unicode_literals

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CierreSesionCaja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.FloatField(default=0)),
                ('bill100', models.IntegerField(blank=True, default=0, null=True)),
                ('bill50', models.IntegerField(blank=True, default=0, null=True)),
                ('bill20', models.IntegerField(blank=True, default=0, null=True)),
                ('bill10', models.IntegerField(blank=True, default=0, null=True)),
                ('bill5', models.IntegerField(blank=True, default=0, null=True)),
                ('bill2', models.IntegerField(blank=True, default=0, null=True)),
                ('bill1', models.IntegerField(blank=True, default=0, null=True)),
                ('enmonedas', models.FloatField(blank=True, default=0, null=True)),
                ('deposito', models.FloatField(blank=True, default=0, null=True)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('sesion',),
                'db_table': 'cashregisters_closesessions',
                'verbose_name': 'Cash Register Closed Session',
                'verbose_name_plural': 'Cash Register Closed Sessions',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ruc', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.TextField(blank=True, null=True)),
                ('telefono', models.CharField(blank=True, max_length=50, null=True)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ('nombre',),
                'db_table': 'customers',
                'verbose_name': 'Customer',
                'verbose_name_plural': 'Customers',
            },
        ),
        migrations.CreateModel(
            name='DetalleIngresoProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('costo', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('valor', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
            ],
            options={
                'ordering': ('purchase', 'producto'),
                'db_table': 'purchase_details',
                'verbose_name': 'Purchase Detail',
                'verbose_name_plural': 'Purchase Details',
            },
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('pvp', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('valor', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('iva', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('subtotal', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
            ],
            options={
                'ordering': ('venta',),
                'db_table': 'sales_details',
                'verbose_name': 'Sale Detail',
                'verbose_name_plural': 'Sales Details',
            },
        ),
        migrations.CreateModel(
            name='IngresoProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numerodocumento', models.CharField(blank=True, max_length=20, null=True)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('descripcion', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ('fecha',),
                'db_table': 'purchases',
                'verbose_name': 'Purchase',
                'verbose_name_plural': 'Purchases',
            },
        ),
        migrations.CreateModel(
            name='InventarioReal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('costo', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('valor', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
            ],
            options={
                'ordering': ('producto',),
                'db_table': 'inventories',
                'verbose_name': 'Inventory',
                'verbose_name_plural': 'Inventories',
            },
        ),
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
                ('nombre', models.CharField(max_length=100)),
                ('icono', models.CharField(max_length=100)),
                ('descripcion', models.CharField(max_length=200)),
                ('orden', models.IntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('grupo', 'orden'),
                'db_table': 'modules',
                'verbose_name': 'Module',
                'verbose_name_plural': 'Modules',
            },
        ),
        migrations.CreateModel(
            name='ModuloGrupo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(blank=True, max_length=200)),
                ('orden', models.IntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('orden', 'nombre'),
                'db_table': 'modules_groups',
                'verbose_name': 'Modules Group',
                'verbose_name_plural': 'Modules Groups',
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=10)),
                ('codigobarra', models.CharField(blank=True, max_length=20, null=True)),
                ('descripcion', models.CharField(max_length=50)),
                ('unidadmedida', models.CharField(default=b'UNO', max_length=3)),
                ('alias', models.CharField(max_length=20)),
                ('pvp', models.DecimalField(decimal_places=2, max_digits=11)),
                ('activo', models.BooleanField(default=True)),
                ('esfavorito', models.BooleanField(default=False)),
                ('foto', models.FileField(upload_to=b'fotoaf/%Y/%m/%d')),
            ],
            options={
                'ordering': ('codigo',),
                'db_table': 'products',
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
            },
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=300)),
                ('alias', models.CharField(blank=True, max_length=100, null=True)),
                ('identificacion', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.CharField(blank=True, max_length=100, null=True)),
                ('celular', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'ordering': ('nombre',),
                'db_table': 'suppliers',
                'verbose_name': 'Supplier',
                'verbose_name_plural': 'Suppliers',
            },
        ),
        migrations.CreateModel(
            name='SesionCaja',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField()),
                ('fondo', models.DecimalField(decimal_places=2, max_digits=11)),
                ('facturaempieza', models.IntegerField(default=0)),
                ('facturatermina', models.IntegerField(default=0)),
                ('abierta', models.BooleanField(default=True)),
                ('cajero', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ('-fecha',),
                'db_table': 'cashregisters_sessions',
                'verbose_name': 'Cash Register Session',
                'verbose_name_plural': 'Cash Register Sessions',
            },
        ),
        migrations.CreateModel(
            name='TipoProducto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('inicial', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('inicial',),
                'db_table': 'categories',
                'verbose_name': 'Product Category',
                'verbose_name_plural': 'Product Categories',
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=20)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('subtotal', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('iva', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('pago', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('devolucion', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=11)),
                ('valida', models.BooleanField(default=True)),
                ('motivoanulacion', models.CharField(blank=True, max_length=200, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Cliente')),
                ('sesioncaja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.SesionCaja')),
                ('usuarioanula', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('fecha',),
                'db_table': 'sales',
                'verbose_name': 'Sale',
                'verbose_name_plural': 'Sales',
            },
        ),
        migrations.AddField(
            model_name='producto',
            name='tipoproducto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.TipoProducto'),
        ),
        migrations.AddField(
            model_name='modulo',
            name='grupo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.ModuloGrupo'),
        ),
        migrations.AddField(
            model_name='inventarioreal',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Producto'),
        ),
        migrations.AddField(
            model_name='ingresoproducto',
            name='proveedor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Proveedor'),
        ),
        migrations.AddField(
            model_name='detalleventa',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Producto'),
        ),
        migrations.AddField(
            model_name='detalleventa',
            name='venta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Venta'),
        ),
        migrations.AddField(
            model_name='detalleingresoproducto',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.Producto'),
        ),
        migrations.AddField(
            model_name='detalleingresoproducto',
            name='purchase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.IngresoProducto'),
        ),
        migrations.AddField(
            model_name='cierresesioncaja',
            name='sesion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.SesionCaja'),
        ),
    ]
