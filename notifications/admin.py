from django.contrib import admin

# Register your models here.
from notifications.models import (
    SMSNotificationTransaction,
)



class SMSNotificationTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'remote_id',
        'status',
        'dest_number',
        'user_response',
    ]
    list_filter = (
        'status',
    )
    search_fields = (
        'remote_id',
        'dest_number',
        'user_response',
    )


admin.site.register(SMSNotificationTransaction, SMSNotificationTransactionAdmin)

