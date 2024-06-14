from django.contrib import admin

from sales.models import Customer, CustomerStatus, DecisionMaker

# Register your models here.

admin.site.register(Customer)
admin.site.register(CustomerStatus)
admin.site.register(DecisionMaker)
