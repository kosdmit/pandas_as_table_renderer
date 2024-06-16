# Pandas НЕ для анализа данных

## Введение

В среде питонистов библиотека Pandas пользуется большой популярностью и по большей мере известна в контексте DataSciense и анализа данных, как инструмент для работы с большими объемами данных. Как следует из русскоязычной википедии: "**pandas** — это программная библиотека на языке Python для обработки и анализа данных." Наверное не один Jupyter ноутбук не обходится без использования пандосовских DataFrame'ов. На самом деле, DataFrame пандас позволяет не только всячески манипулировать данными, но и выводить их в нужном формате, предоставляя широкие возможности для кастомизации. Например, использовали ли вы объекты класса `Styler` входящего в состав Pandas? Мне показалось интересным взлянуть на Pandas с этой стороны.

На практике очень многие бизнес-задачи подразумевают работу с двумерными массивами данных или проще говоря - таблицами. Как следствие, возникает потребность представлять такие данные в виде удобном для восприятия человеком. Поэтому будет интерсено поговорить о подходах к рендеренгу таблиц в контексте веб-приложения на Python.

Актуальности данной теме добавляет тот факт, что подобной информации довольно мало как в интернете, так и в профессиональной литературе (возможность рендеринга таблиц в html не упоминается и в указанной выше [статье](https://ru.wikipedia.org/wiki/Pandas) википедии).

## Проблема

Мы хотим отображать имеющиеся данные в виде html таблицы.

Часто одни и те же данные нужно представить в разных вариациях, например отобразить на странице сайта, в email сообщении или формате Excel. Когда я начинал работу над одним из прошлых проектов, я столкнулся с трудно-поддерживаемыми, толстыми шаблонами веб-страниц, которые содержали html разметку для отображения таблиц с большим количеством данных. К тому же, html шаблоны могли иметь различные вариации например для email уведомлений и тд. Такой подход вызывает трудности при изменении структуры таблицы или данных.

*Все последующие манипуляции будем проводить в контексте приложения на Django. В качестве адаптера БД имеется модель `Customer`, в качестве http представления имеем - `CustomerListView`.
Код проекта с начальными условиями доступен на GitHub - [commit# 8fdf785](https://github.com/kosdmit/pandas_as_table_renderer/tree/8fdf785e0e715329d7390cae17c68b23cf8562a0).*

Решение в лоб - передать в контекст страницы итерируемый объект содержащий строки данных, и средствами шаблонизатора итерироваться по нему формируя html код таблицы строка за строкой.

✅ Не требует использования дополнительных библиотек
❌ "Толстые" шаблоны таблиц
❌ Затруднена поддержка и внесение изменений
❌ Повторение работы при необходимости добавить вариацию таблицы (email, Excel и тд.)

## Используем DataFrame

Поскольку pandas уже входил в технологический стек проекта, было принято решение задействовать эту библиотеку для рендеринга таблиц в html.

DataFrame это внутренняя структура Pandas для хранения таблицы и проведения операций над ней. Создадим новый объект DataFrame, передав нужные данные в конструктор класса, и отрендерим html воспользовавшись методом датафрейма - `to_html()`:

```python
# views.py

class CustomerListView(ListView):
    model = Customer
    paginate_by = 10

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = self.get_html_table(context['object_list'])
        return context

    def get_html_table(self, object_list: QuerySet):
        df = pd.DataFrame(
            data=object_list.values_list(),
            columns=[field.verbose_name for field in object_list.model._meta.get_fields()],
        )
        return df.to_html()
```

Метод `get_html_table()` возвращает html код таблицы принимая на вход объект типа QuerySet - `object_list` из контекcта ListView Django.

Конструктор класса DataFrame может принимать итерируемый объект который содержит входные данные и список наименований столбцов.
Поэтому передаем данные в DataFrame воспользовавшись методом QuerySet.values_list() для представления объектов БД в виде кортежей со значениями атрибутов объекта.

Таким образом, мы получили html таблицу написав миниатюрный метод состоящий из нескольких строк кода. Хотя, стоит отметить, что в таком виде таблица не будет иметь какой либо стилизации. Убедимся в этом добавив полученный html в шаблон страницы, и взглянем на неё:

```html
# customer_list.html

{% extends 'base.html' %}

{% block content %}
  <div class="col-6">
    {{ table|safe }}
  </div>
{% endblock %}
```

![Изображение 1. Таблица без стилизации](./assets/1.PNG)

*Код проекта из этого раздела доступен на GitHub - [commit# 2005e31](https://github.com/kosdmit/pandas_as_table_renderer/tree/2005e31e9314ce67bda388aca7240ac85474d8d9).*

## Используем средства стилизации

На самом деле метод `DataFrame.to_html` может принимать определенный перечень аргументов для обеспечения удобочитаемости таблицы на выходе. Например можно настроить ширину границ ячеек, отображение индекса, заполнение пустых ячеек, выравнивание наименований столбцов и т.д. (с полным перечнем возможностей можно ознакомиться на соответсвующей странице в [документации](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_html.html)).

```python
# views.py
# def get_html_table(queryset):

return df.to_html(
            classes='table table-striped table-hover',
            border=0,
            index=False,
            na_rep='-',
            justify='left',
            columns=(
                Customer.id.field.verbose_name,
                Customer.status.field.verbose_name,
                Customer.name.field.verbose_name,
                Customer.source.field.verbose_name,
                Customer.target_volume.field.verbose_name,
                Customer.problematic.field.verbose_name,
            ),
        )
```

Аргумент `columns` определяет отображаемые столбцы таблицы, таким образом можно использовать один экземпляр DataFrame в различных сценариях вывода, когда требуется ограничить количество отображаемой информации (например для отправки таблицы в email).

С помощью аргумента `classes` можно оперделять css классы html элемента `<table>` и гибко управлять отображением таблицы с помощью css-правил. В приведенном примере я использую готовые стили css-библиотеки Bootstrap 5 для быстрой стилизации таблицы. Таким образом можжно получить результат соотвтветсвующий стилю вашего проекта.

![ Изображение 2. Стилизация таблицы](assets/2.PNG)

✅ Логика рендеринга объектов инкапсулирется в соответствующие классы
✅ Возможность изменения структуры таблиц без редактирования html шаблонов
❌ Ограниченные возможности контроля рендеринга html и стилизации

*Код проекта из этого раздела доступен на GitHub - [commit# 8108dd0](https://github.com/kosdmit/pandas_as_table_renderer/tree/8108dd08aa063fca0ae7b1b7eb9e70416357704a).*

## Используем Styler

В предыдущем разделе мы получили html код который можно использовать например для отображения таблиц в email письмах. Но чаще всего задачи разработки требуют более широкого контроля над процессом server-side рендеринга.

Класс Styler - это интрумент для гибкого контроля над процессом экспорта струтур данных Pandas в различные сторонние форматы. Помимо рендеринга html, класс Styler позволяет экспортировать данные в формат Excel и др. Это весьма удобно, ведь в практике автоматизации бизнес-задач, часто необходима возможность представления данных как в html так и формате xlsx и др.

```python
# views.py
# class CustomerListView(ListView):

def get_html_table(queryset: QuerySet) -> str:
    df = pd.DataFrame(
        data=queryset.values_list(),
        columns=[field.verbose_name for field in queryset.model._meta.get_fields()],
    )

    columns = ('id', 'status', 'name', 'source', 'target_volume', 'problematic')  # Список отображаемых столбцов

    styler = Styler(df)
    styler.format(na_rep='-')
    styler.hide(axis='index')
    styler.hide(
        subset=[field.verbose_name for field in Customer._meta.get_fields() if field.name not in columns],
        axis='columns',
    )

    return styler.to_html(table_attributes='class="table table-striped table-hover"')
```

Обновленный метод возвращает идентичную таблицу, но может показаться немного более сложным по сравнению с тем, что мы использовали ранее. Не смотря на это, такой вариант является более предпочтительным, т.к. дает намного больше возможностей контроля, в чем мы убедимся далее.

Контруктор класса Styler принимает в качестве обязательного аргумента DataFrame Pandas. После инициалзации объект класса предоставляет широкий набор интрументов стилизации. C полным перечнем методов класса Styler вы можете ознакомиться в соответствующем разделе [документации](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.html).

*Код проекта из этого раздела доступен на GitHub - [commit# 8ad47cc](https://github.com/kosdmit/pandas_as_table_renderer/tree/8ad47cc3b87b4426cd08bce1878994863652ba6c).*

✅ Логика рендеринга объектов инкапсулирется в соответствующие классы
✅ Возможность изменения структуры таблиц без редактирования html шаблонов
✅ Широкие возможности контроля рендеринга html и стилизации

## Препарируем Styler

Мы достигли определнного прогресса в деле оптимизации подхода к рендеренгу табличных данных в html. А теперь переходим к наиболее интерсной части, в которой мы немного погрузимся в исходный код Pandas.

Перед этим поставим задачу - отрендерить чуть более интерактивную html-таблицу. Сделаем так, чтобы при клике на строку таблицы, которая по сути явлется представлением объекта ORM, открывалась страница с подробной информацией об объекте.

Под капотом Pandas использует стандарный для индустрии подход с использованием популярного шаблонизатора Jinja2. Посмотрим на шаблоны Jinja2 использующиеся для рендеренга html. Шаблоны используемые для вывода данных хранятся в модуле Pandas `io.formats`, папка `templates`. Таким образом, интересующий нас шаблон `html_table.tpl` можно найти в следующей дирктории:`Pyhton/Lib/site-packages/pandas/io/formats/templates/html_table.tpl`, где `Python` - директория установки вашего интерпретатора Python.

```html
# venv/Lib/site-packages/pandas/io/formats/templates/html_table.tpl

...
{% block tr scoped %}
    <tr>
{% if exclude_styles %}
{% for c in r %}{% if c.is_visible != False %}
      <{{c.type}} {{c.attributes}}>{{c.display_value}}</{{c.type}}>
{% endif %}{% endfor %}
{% else %}
{% for c in r %}{% if c.is_visible != False %}
      <{{c.type}} {%- if c.id is defined %} id="T_{{uuid}}_{{c.id}}" {%- endif %} class="{{c.class}}" {{c.attributes}}>{{c.display_value}}</{{c.type}}>
{% endif %}{% endfor %}
{% endif %}
    </tr>
{% endblock tr %}
...
```

Для краткости, выше приведен только фрагмент файла `html_table.tpl` отвечающий за рендер элемента `<tr>`. Именно с этим блоком нам предстоит поработать, если мы хотим сделать строки таблицы кликабельными. Из приведенного фрагмента видно, что разработчики Pandas не предусмотрели возможность прямо добалять атрибуты для html-элемента `<tr>`, поэтому нам предстоит создать свой шаблон `html_table.tpl` расширяющий существующий и, используя механизм наследования шаблонов Jinja2, переопределить блок `{% block tr scoped %}`:

```html
# sales/templates/pandas/html_table.tpl

{% extends 'venv/Lib/site-packages/pandas/io/formats/templates/html_table.tpl' %}

{% block tr scoped %}
    <tr {{ tr_attributes }}> <!-- customized element -->
{% if exclude_styles %}
{% for c in r %}{% if c.is_visible != False %}
      <{{c.type}} {{c.attributes}}>{{c.display_value}}</{{c.type}}>
{% endif %}{% endfor %}
{% else %}
{% for c in r %}{% if c.is_visible != False %}
      <{{c.type}} {%- if c.id is defined %} id="T_{{uuid}}_{{c.id}}" {%- endif %} class="{{c.class}}" {{c.attributes}}>{{c.display_value}}</{{c.type}}>
{% endif %}{% endfor %}
{% endif %}
    </tr>
{% endblock tr %}

{% block after_table %}
  {{ super() }}
  <script>
    function openDetailView($tr) {
      let pk = $tr.find('td.col0').text();
      window.location = `/sales/customer/${pk}/detail`;
    }
  </script>
{% endblock after_table %}
```

Новый шаблон `html_table.tpl` расширяет стандартный шаблон Pandas. Блок `{% block tr scoped %}` переопределяет аналогичный блок из стандарного шаблона, и даёт возможность добавлять атрибуты для html-элемента `<tr>` передавая соответсвующую переменную в контекст рендеринга. Далее мы добаляем функцию JavaScript, которая должна вызываться при клике на строку таблицы и перенаправлять пользователя на соответсвующую страницу.

Теперь создадим кастомный класс-стайлер который будет использовать новый шаблон и непосредственно определим атрибут `onclick` элемента `<tr>`:

```python
# views.py
# class CustomerListView(ListView):

def get_html_table(queryset: QuerySet) -> str:
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
```

Для первой цели класс `Styler` предоставляет специальный метод - `from_custom_template()`, который возвращает новый класс - `MyStyler`. Новый класс наследуется от стандартного `Styler`, но обладает атрибутами класса определющими кастомное окружение и  шаблоны Jinja2.

Теперь стайлер использует для рендеринга новый шаблон, который позволяет использовать переменную `tr_attributes`, передаем ее в контект шаблонизатора через именнованный аргумент метода `Styler.to_html()`.

Исользуя переменную `tr_attributes` мы добавляем атрибуты `onclick` и `style` всем элементам `<tr>` нашей таблицы.

Первый атрибут определяет повдение браузера при клике на строку. В нашем случае вызывается упомянутая выше функция - `openDetailView($tr)`. При этом в качестве аргумента передается сам DOM-объект, для удобства обернутый в jQuery-селектор (я использую JavaScript библиотеку jQuery для краткости и повышения читаемости кода, хотя это не обязательно).

Атрибут `style`, в нашем случае, обеспечивает правильное поведение указателя мышы при наведении на кликабельный объект.

*Код проекта из этого раздела доступен на GitHub - [commit#](https://github.com/kosdmit/pandas_as_table_renderer/).*

