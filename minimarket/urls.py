"""minimarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from store import (views, productos, proveedores, inventarios, ingresoinv, reportes, ventas,
                   clientes, caja, cons_compras, cons_ventas, estadisticas)

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # Menu Raiz (por el momento redirecciona al Admin)
    url(r'^$', views.index),
    url(r'^login$', views.login_user),
    url(r'^logout$', views.logout_user),

    # GESTION DE PRODUCTOS
    url(r'^productos$', productos.view),

    # PROVEEDORES
    url(r'^proveedores$', proveedores.view),

    # GESTION DE INVENTARIO REAL
    url(r'^inventarios$', inventarios.view),

    # INGRESO DE PRODUCTOS
    url(r'^ingresoinv$', ingresoinv.view),

    # REPORTES
    url(r'^reportes$', reportes.view),

    # CLIENTES
    url(r'^clientes$', clientes.view),

    url(r'^caja', caja.view),

    # CONSULTA DE VENTAS
    url(r'^cons_ventas', cons_ventas.view),

    # CONSULTA DE COMPRAS
    url(r'^cons_compras', cons_compras.view),

    url(r'^pass$', views.passwd),

    # ESTADISTICAS Y GRAFICOS
    url(r'^estadisticas$', estadisticas.view),

    # CONSUMO DE INVENTARIOS
    url(r'^ventas$', ventas.view),

    # url(r'^api$', 'acc.api.view),
    # url(r'^print/(?P<referencia>.+)/(?P<id>\d+)$', 'acc.printdoc.view),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
