{%- macro get_config(configname, from) -%}
{%- if configname in from -%}
{{ print_group(configname, from[configname]) }}
{%- endif -%}
{%- endmacro -%}

{%- macro print_group(key, value, width=0) -%}
{%- if value is string or value is number -%}
{{ key }}: {{ print_single(value) | indent(width=width+2, indentfirst=true) }}
{%- elif value is mapping -%}
{{ key }}:
{{ print_dict(value) | indent(width=width+2, indentfirst=true)  }}
{%- elif value is iterable -%}
{{ key }}:
{{ print_list(value) | indent(width=width+2, indentfirst=true)  }}
{%- endif -%}
{%- endmacro -%}

{%- macro print_single(value) -%}
{{ value }}
{%- endmacro -%}

{%- macro print_list(items, width=0) -%}
{%- for intravalue in items -%}
{%- if intravalue is string or intravalue is number -%}
- {{ print_single(intravalue) | indent(width=width+2) }}
{% elif intravalue is mapping -%}
- {{ print_dict(intravalue) | indent(width=width+2) }}
{% endif -%}
{%- endfor -%}
{%- endmacro -%}

{%- macro print_dict(items, width=0) -%}
{%- for intrakey, intravalue in items.iteritems() -%}
{{ print_group(intrakey, intravalue, width=width) }}
{% endfor -%}
{%- endmacro -%}
