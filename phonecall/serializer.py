from datetime import date, time
from .models import PhoneCall
from rest_framework import serializers


class PhoneCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneCall
        fields = ('type', 'timestamp', 'call_id', 'source', 'destination')
