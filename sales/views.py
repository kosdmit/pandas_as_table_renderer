import pandas as pd
from django.db.models import QuerySet
from django.views.generic import ListView

from sales.models import Customer


# Create your views here.


class CustomerListView(ListView):
    model = Customer
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_table'] = self.get_html_table(queryset=context['object_list'])
        return context

    @staticmethod
    def get_html_table(queryset: QuerySet) -> str:
        """
        Представляет объекты из получаемого QuerySet в виде html таблицы

        :param queryset: Django QuerySet
        :returns (str): HTML код таблицы
        """
        df = pd.DataFrame(
            data=queryset.values_list(),
            columns=[field.verbose_name for field in queryset.model._meta.get_fields()],
        )
        return df.to_html(index=False)
