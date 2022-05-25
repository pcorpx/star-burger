from django.db import models
from django.utils import timezone


class Location(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True
    )
    lat = models.FloatField(null=True, verbose_name='Широта')
    lon = models.FloatField(null=True, verbose_name='Долгота')
    last_update = models.DateTimeField(verbose_name='Получены в',
                                       default=timezone.now)

    class Meta:
        verbose_name = 'Место'
        verbose_name_plural = 'Места'

    def __str__(self):
        return f"{self.address}"
