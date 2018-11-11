import re
from datetime import date, time
from decimal import Decimal, ROUND_UP

from rest_framework import exceptions

from .models import PhoneCall


def format_duration(value):
    hours, rem = divmod(value.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{}h{}m{}s".format(hours, minutes, seconds)


def format_price(value):
    value = Decimal(value).quantize(Decimal('0.00'), rounding=ROUND_UP)
    return "R$ {}".format(str(value).replace('.', ','))


def get_phone_data(phone_call_end):
    phone_call_start = PhoneCall.objects.get(type='start', call_id=phone_call_end.call_id)
    call_start_time = time(phone_call_start.timestamp.hour, phone_call_start.timestamp.minute,
                           phone_call_start.timestamp.second)
    call_start_date = date(phone_call_start.timestamp.year, phone_call_start.timestamp.month,
                           phone_call_start.timestamp.day)
    data = {
        'call_price': format_price(phone_call_end.price),
        'call_duration': format_duration(phone_call_end.duration),
        'call_start_time': call_start_time,
        'call_start_date': call_start_date,
        'destination': phone_call_start.destination
    }

    return data


def validate_params(source, month, year):
    if not source or not re.match('^[\d]{11}$', source):
        raise exceptions.ValidationError(detail='Invalid Source value.')
    try:
        date(int(year), int(month), 1)
    except (ValueError, TypeError):
        raise exceptions.ValidationError(detail='Invalid month/year value.')
