from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.utils import timezone

from escalas.models import ReservationToken

from escalas.services import reservar_escala, remover_escala
from escalas.models import Escala, Turno

@login_required
def lista_escalas(request):
    escalas = (
        Escala.objects
        .select_related('usuario', 'turno')
        .order_by('data', 'turno__hora_inicio')
    )

    turnos = Turno.objects.all()

    return render(
        request,
        'escalas/lista_escalas.html',
        {
            'escalas': escalas,
            'turnos': turnos,
        }
    )

@login_required
def reservar(request):
    if request.method != 'POST':
        return redirect('lista_escalas')

    try:
        reservar_escala(
            usuario=request.user,
            data=request.POST['data'],
            turno_id=request.POST['turno_id']
        )
    except Exception as e:
        return HttpResponse(
            f'<p class="msg-error">{e}</p>',
            status=400
        )

    escalas = Escala.objects.select_related('usuario', 'turno')

    html = render_to_string(
        'escalas/_tabela_escalas.html',
        {'escalas': escalas, 'request': request}
    )

    return HttpResponse(html)

@login_required
def remover(request, escala_id):
    if request.method != 'POST':
        return redirect('lista_escalas')

    remover_escala(
        usuario=request.user,
        escala_id=escala_id
    )

    escalas = Escala.objects.select_related('usuario', 'turno')

    html = render_to_string(
        'escalas/_tabela_escalas.html',
        {'escalas': escalas, 'request': request}
    )

    return HttpResponse(html)

@login_required
def heartbeat_token(request):
    try:
        token = request.user.reservation_token
    except ReservationToken.DoesNotExist:
        return HttpResponse('SEM_TOKEN', status=200)

    if not token.esta_valido():
        return HttpResponse('EXPIRADO', status=409)

    token.renovar()
    return HttpResponse('OK', status=200)
