from django.core.exceptions import PermissionDenied

def pode_visualizar(usuario):
    return usuario.is_authenticated

def pode_criar_escala(usuario):
    if not usuario.is_authenticated:
        return False

    if usuario.role in ['R1', 'R2', 'ADMIN']:
        return True

    return False

def pode_remover_escala(usuario, escala):
    if usuario.role == 'ADMIN':
        return True

    if usuario.role in ['R1', 'R2'] and escala.usuario == usuario:
        return True

    return False

def pode_ignorar_token(usuario):
    return usuario.role == 'ADMIN'

def exigir_criacao(usuario):
    if not pode_criar_escala(usuario):
        raise PermissionDenied(
            'Você não tem permissão para criar escalas.'
        )


def exigir_remocao(usuario, escala):
    if not pode_remover_escala(usuario, escala):
        raise PermissionDenied(
            'Você não pode remover esta escala.'
        )

