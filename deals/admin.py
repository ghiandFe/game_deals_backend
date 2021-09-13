from django.contrib import admin

from .models import Deal, Store


# Register your models here.

class DealAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'store',
                    'sale_price', 'normal_price', 'is_on_sale')


admin.site.register(Deal, DealAdmin)
admin.site.register(Store)