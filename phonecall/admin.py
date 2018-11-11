from django.contrib import admin

from phonecall.models import PhoneCall


@admin.register(PhoneCall)
class PhoneCallAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'timestamp', 'call_id', 'source', 'destination')
