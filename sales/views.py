from django.views.generic import ListView

from sales.models import Customer


# Create your views here.


class CustomerListView(ListView):
    model = Customer
