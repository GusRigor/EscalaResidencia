from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import time, datetime, timedelta


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

User = settings.AUTH_USER_MODEL

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

