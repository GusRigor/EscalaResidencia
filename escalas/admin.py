from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Escala, Turno, ReservationToken

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'codigo',
        'hora_inicio',
        'hora_fim',
        'atravessa_dia',
    )

    list_filter = ('atravessa_dia',)
    search_fields = ('nome', 'codigo')
    ordering = ('hora_inicio',)

    fieldsets = (
        ('Identificação', {
            'fields': ('nome', 'codigo')
        }),
        ('Horário', {
            'fields': ('hora_inicio', 'hora_fim', 'atravessa_dia')
        }),
    )

@admin.register(Escala)
class EscalaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'role_usuario',
        'data',
        'turno',
        'criada_em',
    )

    list_filter = (
        'data',
        'turno',
        'usuario__role',
    )

    search_fields = (
        'usuario__username',
        'usuario__first_name',
    )

    date_hierarchy = 'data'
    ordering = ('-data', 'turno__hora_inicio')

    autocomplete_fields = ('usuario', 'turno')

    readonly_fields = ('criada_em',)

    fieldsets = (
        ('Escala', {
            'fields': ('usuario', 'data', 'turno')
        }),
        ('Auditoria', {
            'fields': ('criada_em',)
        }),
    )

    def role_usuario(self, obj):
        return obj.usuario.role

    role_usuario.short_description = 'Tipo'

@admin.register(ReservationToken)
class ReservationTokenAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'role_usuario',
        'token_curto',
        'esta_valido_admin',
        'valido_ate',
        'ultimo_heartbeat',
    )

    list_filter = (
        'usuario__role',
    )

    search_fields = (
        'usuario__username',
        'usuario__first_name',
    )

    ordering = ('-ultimo_heartbeat',)

    readonly_fields = (
        'token',
        'criado_em',
        'ultimo_heartbeat',
    )

    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Token', {
            'fields': ('token',)
        }),
        ('Validade', {
            'fields': ('valido_ate', 'ultimo_heartbeat')
        }),
        ('Auditoria', {
            'fields': ('criado_em',)
        }),
    )

    # 🔎 Helpers visuais

    def role_usuario(self, obj):
        return obj.usuario.role

    role_usuario.short_description = 'Tipo'

    def token_curto(self, obj):
        return str(obj.token)[:8]

    token_curto.short_description = 'Token'

    def esta_valido_admin(self, obj):
        return obj.esta_valido()

    esta_valido_admin.boolean = True
    esta_valido_admin.short_description = 'Válido'

    # 🔒 Segurança
    def has_add_permission(self, request):
        return False
