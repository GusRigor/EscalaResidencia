import calendar
from datetime import datetime

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
    
    if not request.user.is_admin():
        escalas = escalas.filter(usuario=request.user)

    turnos = Turno.objects.all()

    return render(
        request,
        'escalas/lista_escalas.html',
        {
            'escalas': escalas,
            'turnos': turnos,
            'today': timezone.localdate(),
        }
    )

@login_required
def reservar(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    data = request.POST.get('data')
    turno_id = request.POST.get('turno_id')

    if not data or not turno_id:
        return HttpResponse(
            '<p class="msg-error">Dados inválidos.</p>',
            status=400
        )

    try:
        data = datetime.strptime(data, '%Y-%m-%d').date()
    except ValueError:
        print("DATA INVÁLIDA RECEBIDA:", data)
        return HttpResponse(
            '<p class="msg-error">Data inválida.</p>',
            status=400
        )

    try:
        reservar_escala(
            usuario=request.user,
            data=data,
            turno_id=turno_id
        )
    except ValidationError as e:
        print("VALIDATION ERROR:", e)
        return HttpResponse(
            f'<p class="msg-error">{e.message}</p>',
            status=400
        )
    except Exception as e:
        print("ERRO INESPERADO:", e)
        return HttpResponse(
            '<p class="msg-error">Erro inesperado.</p>',
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

def calendario_mensal(request):
    hoje = timezone.localdate()
    ano = hoje.year
    mes = hoje.month

    cal = calendar.Calendar(firstweekday=0)
    dias_mes = cal.monthdatescalendar(ano, mes)

    escalas = (
        Escala.objects
        .select_related('usuario', 'turno')
        .filter(data__month=mes, data__year=ano)
    )

    # Agrupa escalas por data
    mapa = {}
    for escala in escalas:
        mapa.setdefault(escala.data, []).append(escala)

    return render(
        request,
        'calendario.html',
        {
            'dias_mes': dias_mes,
            'mapa': mapa,
            'hoje': hoje,
        }
    )
