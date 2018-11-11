from datetime import datetime

from django.test import TestCase
from freezegun import freeze_time
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from phonecall.models import PhoneCall


class TestCreatePhoneCall(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_phone_call_start(self):
        data = {
            "type": "start",
            "timestamp": "2018-12-30T12:00:00",
            "call_id": "008",
            "source": 19982065330,
            "destination": 19982055500
        }
        response = self.client.post(reverse('phonecall-list'), data, format='json')
        assert response.status_code == 201
        assert PhoneCall.objects.exists()
        assert PhoneCall.objects.first().type == 'start'
        assert PhoneCall.objects.first().call_id == '008'

    def test_create_phone_call_end(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 12, 30, 12, 0, 0), call_id='008',
                                 source=19982065330, destination=19982055500)
        data = {
            "type": "end",
            "timestamp": "2018-12-30T12:55:00",
            "call_id": "008"
        }
        response = self.client.post(reverse('phonecall-list'), data, format='json')
        assert response.status_code == 201
        assert PhoneCall.objects.count() == 2
        assert PhoneCall.objects.last().type == 'end'
        assert PhoneCall.objects.last().price > 0
        assert PhoneCall.objects.last().duration.seconds == 55 * 60

    def test_create_phone_call_end_without_start(self):
        data = {
            "type": "end",
            "timestamp": "2018-12-30T12:55:00",
            "call_id": "008"
        }
        response = self.client.post(reverse('phonecall-list'), data, format='json')
        assert response.status_code == 404
        assert not PhoneCall.objects.exists()


class TestPhoneCallBill(TestCase):

    def setUp(self):
        PhoneCall.objects.create(type='start', timestamp=datetime(2018, 10, 30, 12, 0, 0), call_id='008',
                                 source=19982065330, destination=19982055500)
        PhoneCall.objects.create(type='end', timestamp=datetime(2018, 10, 30, 12, 5, 0), call_id='008')

    @freeze_time("2018-11-05")
    def test_phonecall_bill(self):
        response = self.client.get(reverse('phonecalls-bill-list'), {'source': 19982065330})
        assert response.data['total_price'] == 'R$ 0,81'
        assert response.data['calls'][0]['destination'] == 19982055500
        assert response.data['calls'][0]['call_duration'] == '0h5m0s'

    @freeze_time("2018-12-05")
    def test_phonecall_bill_with_date(self):
        response = self.client.get(reverse('phonecalls-bill-list'), {'source': 19982065330, 'month': 10, 'year': 2018})
        assert response.data['total_price'] == 'R$ 0,81'
        assert response.data['calls'][0]['destination'] == 19982055500
        assert response.data['calls'][0]['call_duration'] == '0h5m0s'

    @freeze_time("2018-12-05")
    def test_phonecall_bill_with_no_results(self):
        response = self.client.get(reverse('phonecalls-bill-list'), {'source': 19982065330, 'month': 9, 'year': 2018})
        assert not response.data['calls']

    def test_phonecall_bill_with_invalid_source(self):
        response = self.client.get(reverse('phonecalls-bill-list'), {'source': 1998206533, 'month': 9, 'year': 2018})
        assert response.status_code == 400
        assert response.json()[0] == 'Invalid Source value.'

    def test_phonecall_bill_with_invalid_date(self):
        response = self.client.get(reverse('phonecalls-bill-list'), {'source': 19982065330, 'month': 14, 'year': 2018})
        assert response.status_code == 400
        assert response.json()[0] == 'Invalid month/year value.'
