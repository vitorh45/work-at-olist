from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from .price_calculation import calc_call_price


class PhoneCall(models.Model):
    TYPE_CHOICES = (
        ('start', 'Start'),
        ('end', 'End'),
    )
    type = models.CharField('Type', choices=TYPE_CHOICES, max_length=5)
    timestamp = models.DateTimeField('Timestamp')
    call_id = models.CharField('Call ID', max_length=32)
    source = models.BigIntegerField('Source number', null=True, blank=True, validators=[MinValueValidator(0000000000),
                                                                                        MaxValueValidator(99999999999)])
    destination = models.BigIntegerField('Destination number', null=True, blank=True,
                                         validators=[MinValueValidator(0000000000), MaxValueValidator(99999999999)])
    duration = models.DurationField('Duration time', blank=True, null=True)
    price = models.DecimalField('Price', max_digits=7, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['call_id', 'timestamp']
        verbose_name = 'Phone Call'
        verbose_name_plural = 'Phone Calls'

    def __str__(self):
        return '{} - {}'.format(self.type, self.call_id)


post_save.connect(calc_call_price, sender=PhoneCall)


@receiver(pre_save, sender=PhoneCall)
def check_phone_call_start_existance(sender, **kwargs):
    if kwargs['instance'].type == 'end':
        get_object_or_404(PhoneCall, type='start', call_id=kwargs['instance'].call_id)
