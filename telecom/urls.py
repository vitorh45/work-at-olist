from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from phonecall.views import PhoneCallCreateAPIView, PhoneCallBillViewSet

router = routers.SimpleRouter()

router.register(r'phonecalls', PhoneCallCreateAPIView, 'phonecall')
router.register(r'phonecalls-bill', PhoneCallBillViewSet, 'phonecalls-bill')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^admin/', admin.site.urls)
]
