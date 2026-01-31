from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        R1 = 'R1', 'Residente R1'
        R2 = 'R2', 'Residente R2'
        GUEST = 'GUEST', 'Convidado'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.GUEST
    )

    def is_resident(self):
        return self.role in {self.Role.R1, self.Role.R2}

    def is_admin(self):
        return self.role == self.Role.ADMIN
