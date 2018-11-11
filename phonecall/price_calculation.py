from datetime import time, timedelta, date
from decimal import Decimal, ROUND_UP

from django.conf import settings


def convert_to_time(timestamp):
    return time(timestamp.hour, timestamp.minute, timestamp.second)


def check_same_day(start, end):
    if date(end.year, end.month, end.day) == date(start.year, start.month, start.day):
        return True
    return False


def call_days_duration(start, end):
    return (date(end.year, end.month, end.day) - date(start.year, start.month, start.day)).days


def get_suitable_time(timestamp):
    if time(hour=0, minute=0, second=0) <= timestamp <= settings.STD_TIME_CALL_BEGIN:
        return settings.STD_TIME_CALL_BEGIN
    elif settings.STD_TIME_CALL_END <= timestamp <= time(hour=23, minute=59, second=59):
        return settings.STD_TIME_CALL_END
    else:
        return timestamp


def get_call_duration(start, end):
    diff = end.timestamp - start.timestamp
    days = diff.days
    total_seconds = diff.seconds + (days * 86400)
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    return timedelta(hours=hours, minutes=minutes, seconds=seconds)


def calc_call_price(sender, instance, created, **kwargs):
    if instance.type == 'end':
        from .models import PhoneCall
        if created:
            phone_call_start = PhoneCall.objects.get(type='start', call_id=instance.call_id)

            start_time = get_suitable_time(convert_to_time(phone_call_start.timestamp))
            end_time = get_suitable_time(convert_to_time(instance.timestamp))
            # import pdb
            # pdb.set_trace()
            if check_same_day(phone_call_start.timestamp, instance.timestamp):
                call_end_time = timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)
            else:
                call_end_time = timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second) + \
                                timedelta(
                                    hours=(24 * call_days_duration(phone_call_start.timestamp, instance.timestamp)))

            call_start_time = timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)

            minutes_std = (call_end_time - call_start_time - timedelta(
                hours=(call_days_duration(phone_call_start.timestamp,
                                          instance.timestamp) * settings.DURATION_REDU_TIME))).seconds // 60

            call_duration = get_call_duration(phone_call_start, instance)

            price = settings.STANDING_CHARGE + (settings.STD_CHARGE_MINUTE * minutes_std)
            price = Decimal(price).quantize(Decimal('0.00'), rounding=ROUND_UP)

            instance.duration = call_duration
            instance.price = price
            instance.source = phone_call_start.source
            instance.destination = phone_call_start.destination

            instance.save()
