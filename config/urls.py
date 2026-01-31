from django.contrib import admin
from django.urls import path, include
from escalas.views import calendario_mensal

urlpatterns = [
    path('', include('accounts.urls')),
    path('', calendario_mensal, name='home'),
    path('admin/', admin.site.urls),
    path('escalas/', include('escalas.urls')),
]
