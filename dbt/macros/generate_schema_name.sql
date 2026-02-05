{% macro generate_schema_name(custom_schema_name, node) -%}
  {# Map model-level schema names to the correct BigQuery datasets #}
  {% if custom_schema_name == 'gold' %}
    {{ var('gold_dataset') }}
  {% elif custom_schema_name == 'silver' %}
    {{ var('silver_dataset') }}
  {% elif custom_schema_name is none %}
    {{ target.schema }}
  {% else %}
    {{ custom_schema_name }}
  {% endif %}
{%- endmacro %}
