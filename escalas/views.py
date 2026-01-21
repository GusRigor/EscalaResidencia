from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError

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

    data = request.POST.get('data')
    turno_id = request.POST.get('turno_id')

    try:
        reservar_escala(
            usuario=request.user,
            data=data,
            turno_id=turno_id
        )
        messages.success(request, 'Escala reservada com sucesso.')

    except PermissionDenied as e:
        messages.error(request, str(e))

    except ValidationError as e:
        messages.error(request, e.message)

    return redirect('lista_escalas')

@login_required
def remover(request, escala_id):
    if request.method != 'POST':
        return redirect('lista_escalas')

    try:
        remover_escala(
            usuario=request.user,
            escala_id=escala_id
        )
        messages.success(request, 'Escala removida.')

    except PermissionDenied as e:
        messages.error(request, str(e))

    except ValidationError as e:
        messages.error(request, e.message)

    return redirect('lista_escalas')


