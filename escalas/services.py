from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError

from escalas.models import Escala, Turno
from escalas.permissions import exigir_criacao, exigir_remocao
from escalas.models import ReservationToken, TOKEN_TIMEOUT_MINUTES

from datetime import timedelta

@transaction.atomic
def reservar_escala(*, usuario, data, turno_id):
    """
    Cria uma escala respeitando:
    - permissões
    - token de concorrência
    - regras de sobreposição
    """
    
    # 0️⃣ Valida data
    if data < timezone.localdate():
        raise ValidationError(
            'Não é possível reservar escalas em datas passadas.'
        )

    # 1️⃣ Permissão por papel
    exigir_criacao(usuario)
    
    token = obter_ou_criar_token(usuario)

    # 2️⃣ Token (admin ignora)
    if not usuario.is_admin():
        if not usuario_tem_prioridade(usuario):
            raise PermissionDenied(
                'Outro residente iniciou a reserva antes.'
            )

    # 3️⃣ Buscar turno
    try:
        turno = Turno.objects.select_for_update().get(id=turno_id)
    except Turno.DoesNotExist:
        raise ValidationError('Turno inválido.')

    # 4️⃣ Criar escala (full_clean será chamado no save)
    escala = Escala(
        usuario=usuario,
        data=data,
        turno=turno
    )
    escala.save()

    return escala

@transaction.atomic
def remover_escala(*, usuario, escala_id):
    """
    Remove uma escala respeitando permissões.
    """

    try:
        escala = Escala.objects.select_for_update().get(id=escala_id)
    except Escala.DoesNotExist:
        raise ValidationError('Escala não encontrada.')

    exigir_remocao(usuario, escala)

    escala.delete()

def obter_ou_criar_token(usuario):
    agora = timezone.now()

    token, criado = ReservationToken.objects.get_or_create(
        usuario=usuario,
        defaults={
            'valido_ate': agora + timedelta(minutes=TOKEN_TIMEOUT_MINUTES)
        }
    )

    if not criado:
        token.renovar()

    return token

def usuario_tem_prioridade(usuario):
    token = getattr(usuario, 'reservation_token', None)
    
    print("Verificando prioridade para usuário:", usuario)
    print("Token do usuário:", token)
    print("Token válido até:", token.valido_ate if token else None)
    print("Token está valido", token.esta_valido() if token else None)

    if not token or not token.esta_valido():
        return False

    token_mais_antigo = (
        ReservationToken.objects
        .filter(valido_ate__gte=timezone.now())
        .order_by('criado_em')
        .first()
    )

    return token == token_mais_antigo
