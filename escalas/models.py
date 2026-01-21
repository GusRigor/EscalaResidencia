from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import time, datetime, timedelta
import uuid

User = settings.AUTH_USER_MODEL
TOKEN_TIMEOUT_MINUTES = 5

class Turno(models.Model):
    class Codigo(models.TextChoices):
        MANHA = 'MANHA', 'Manhã (6h)'
        TARDE = 'TARDE', 'Tarde (6h)'
        DIURNO = 'DIURNO', 'Manhã + Tarde (12h)'
        NOITE = 'NOITE', 'Noite (12h)'

    codigo = models.CharField(
        max_length=10,
        choices=Codigo.choices,
        unique=True
    )

    nome = models.CharField(max_length=50)

    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    atravessa_dia = models.BooleanField(
        default=False,
        help_text='Indica se o turno termina no dia seguinte'
    )

    def __str__(self):
        return self.nome

class Escala(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='escalas'
    )

    data = models.DateField(
        help_text='Data de início do turno'
    )

    turno = models.ForeignKey(
        Turno,
        on_delete=models.PROTECT,
        related_name='escalas'
    )

    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data', 'turno__hora_inicio']
        indexes = [
            models.Index(fields=['data']),
        ]

    def __str__(self):
        return f'{self.usuario} - {self.turno} - {self.data}'
    
    def intervalo_real(self):
        """
        Retorna (inicio_datetime, fim_datetime)
        considerando virada de dia
        """
        inicio = datetime.combine(self.data, self.turno.hora_inicio)

        if self.turno.atravessa_dia:
            fim = datetime.combine(
                self.data + timedelta(days=1),
                self.turno.hora_fim
            )
        else:
            fim = datetime.combine(self.data, self.turno.hora_fim)

        return inicio, fim
    
    def conflita_com(self, outra):
        inicio_a, fim_a = self.intervalo_real()
        inicio_b, fim_b = outra.intervalo_real()

        return inicio_a < fim_b and inicio_b < fim_a

    def clean(self):
        """
        Valida:
        - máximo de 2 residentes simultâneos
        """
        from escalas.models import Escala

        inicio, fim = self.intervalo_real()

        escalas_do_dia = Escala.objects.exclude(pk=self.pk)

        conflitos = 0

        for escala in escalas_do_dia:
            inicio_existente, fim_existente = escala.intervalo_real()

            if inicio < fim_existente and inicio_existente < fim:
                conflitos += 1

        if conflitos >= 2:
            raise ValidationError(
                'Já existem dois residentes alocados neste intervalo.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class ReservationToken(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='reservation_token'
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    ultimo_heartbeat = models.DateTimeField(auto_now=True)

    valido_ate = models.DateTimeField()

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'Token {self.token} ({self.usuario})'

    def esta_valido(self):
        return timezone.now() <= self.valido_ate

    def renovar(self):
        agora = timezone.now()
        self.ultimo_heartbeat = agora
        self.valido_ate = agora + timedelta(minutes=TOKEN_TIMEOUT_MINUTES)
        self.save(update_fields=['ultimo_heartbeat', 'valido_ate'])