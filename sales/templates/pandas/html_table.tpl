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