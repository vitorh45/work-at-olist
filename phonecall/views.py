from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, mixins, permissions
from rest_framework.response import Response

from .models import PhoneCall
from .serializer import PhoneCallSerializer
from .utils import get_phone_data, format_price, validate_params


class PhoneCallCreateAPIView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = PhoneCall.objects.all()
    serializer_class = PhoneCallSerializer
    permission_classes = (permissions.AllowAny,)


class PhoneCallBillViewSet(viewsets.ModelViewSet):
    queryset = PhoneCall.objects.all()

    def get_queryset(self):
        source = self.request.query_params.get('source')
        month = self.request.query_params.get('month', timezone.now().month - 1)
        year = self.request.query_params.get('year', timezone.now().year)

        validate_params(source, month, year)
        qs = PhoneCall.objects.filter(type='end', source=source, timestamp__month=month, timestamp__year=year)

        return qs

    def list(self, request, *args, **kwargs):
        result = []
        qs = self.get_queryset()
        if qs:
            total_price = format_price(qs.aggregate(total_price=Sum('price'))['total_price'])

            for phone_call_end in qs:
                result.append(get_phone_data(phone_call_end))

            return Response({'calls': result, 'total_price': total_price})

        return Response({'calls': result})
