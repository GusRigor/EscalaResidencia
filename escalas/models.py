from django.db import models
from datetime import time


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
