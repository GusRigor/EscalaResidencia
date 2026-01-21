from django.utils import timezone
from datetime import timedelta
from escalas.models import ReservationToken, TOKEN_TIMEOUT_MINUTES

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

    if not token or not token.esta_valido():
        return False

    token_mais_antigo = (
        ReservationToken.objects
        .filter(valido_ate__gte=timezone.now())
        .order_by('criado_em')
        .first()
    )

    return token == token_mais_antigo
