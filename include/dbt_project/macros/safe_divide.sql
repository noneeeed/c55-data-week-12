{% macro safe_divide(numerator, denominator) %}
    case
        when {{ denominator }} > 0 then round(({{ numerator }} / {{ denominator }})::numeric, 4)
        else null
    end
{% endmacro %}