from datetime import datetime
from decimal import Decimal, ROUND_UP

from django.conf import settings
from django.http import Http404
from django.test import TestCase

from phonecall.models import PhoneCall


class TestPhoneCallModel(TestCase):

    def test_phone_call_2_days(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 12, 25, 12, 0, 0), call_id='007',
                                 source=19982065330, destination=19982055500)
        PhoneCall.objects.create(type='end', timestamp=datetime(2018, 12, 26, 12, 0, 0), call_id='007')

        assert int(PhoneCall.objects.get(type='end').duration.total_seconds()) == 24 * 3600

        price = Decimal((settings.DURATION_STD_TIME * 60) * 0.09 + 0.36).quantize(Decimal('0.00'), rounding=ROUND_UP)
        assert PhoneCall.objects.get(type='end').price == price

    def test_phone_call_reduced_tariff_same_day(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 12, 25, 4, 0, 0), call_id='007',
                                 source=19982065330, destination=19982055500)
        PhoneCall.objects.create(type='end', timestamp=datetime(2018, 12, 25, 5, 0, 0), call_id='007')

        assert int(PhoneCall.objects.get(type='end').duration.total_seconds()) == 3600
        assert PhoneCall.objects.get(type='end').price == Decimal('0.36')

    def test_phone_call_tariff_mix_same_day(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 12, 25, 5, 58, 0), call_id='007',
                                 source=19982065330, destination=19982055500)
        PhoneCall.objects.create(type='end', timestamp=datetime(2018, 12, 25, 10, 58, 0), call_id='007')

        assert int(PhoneCall.objects.get(type='end').duration.total_seconds()) == 5 * 3600

        price = Decimal((4 * 60 + 58) * 0.09 + 0.36).quantize(Decimal('0.00'), rounding=ROUND_UP)
        assert PhoneCall.objects.get(type='end').price == price

    def test_phone_call_tariff_mix_2_days(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 12, 25, 23, 50, 0), call_id='007',
                                 source=19982065330, destination=19982055500)
        PhoneCall.objects.create(type='end', timestamp=datetime(2018, 12, 26, 7, 50, 0), call_id='007')

        assert int(PhoneCall.objects.get(type='end').duration.total_seconds()) == 8 * 3600

        price = Decimal((1 * 60 + 50) * 0.09 + 0.36).quantize(Decimal('0.00'), rounding=ROUND_UP)
        assert PhoneCall.objects.get(type='end').price == price

    def test_phone_call_reduced_tariff_2_days(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 12, 25, 23, 0, 0), call_id='007',
                                 source=19982065330, destination=19982055500)
        PhoneCall.objects.create(type='end', timestamp=datetime(2018, 12, 26, 1, 0, 0), call_id='007')

        assert int(PhoneCall.objects.get(type='end').duration.total_seconds()) == 7200
        assert PhoneCall.objects.get(type='end').price == Decimal('0.36')

    def test_phone_call_without_start(self):
        phone_call = PhoneCall(type='end', timestamp=datetime(2018, 12, 26, 1, 0, 0), call_id='007')

        self.assertRaises(Http404, lambda: phone_call.save())
