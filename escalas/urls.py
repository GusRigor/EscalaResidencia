from django.urls import path
from escalas import views

urlpatterns = [
    path('', views.lista_escalas, name='lista_escalas'),
    path('reservar/', views.reservar, name='reservar_escala'),
    path('remover/<int:escala_id>/', views.remover, name='remover_escala'),
    path('heartbeat/', views.heartbeat_token, name='heartbeat_token'),
]
