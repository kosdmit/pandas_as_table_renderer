import pandas as pd
from django.db.models import QuerySet
from django.views.generic import ListView, DetailView
from pandas.io.formats.style import Styler

from pandas_as_table_renderer.settings import BASE_DIR
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

        columns = ('id', 'status', 'name', 'source', 'target_volume', 'problematic')  # Список отображаемых столбцов

        CustomStyler = Styler.from_custom_template(
            searchpath=BASE_DIR,
            html_table='sales/templates/pandas/html_table.tpl'
        )

        styler = CustomStyler(df)
        styler.format(na_rep='-')
        styler.hide(axis='index')
        styler.hide(
            subset=[field.verbose_name for field in Customer._meta.get_fields() if field.name not in columns],
            axis='columns',
        )

        return styler.to_html(
            table_attributes='class="table table-striped table-hover"',
            tr_attributes=f'onclick="openDetailView($(this))" style="cursor:pointer;"',
        )


class CustomerDetailView(DetailView):
    template_name = 'sales/customer_detail.html'
    model = Customer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_dict'] = context['object'].__dict__
        return context
