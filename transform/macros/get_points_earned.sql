{% macro get_points_earned(goals_for, goals_against) %}
    case 
        when {{ goals_for }} > {{ goals_against }} then 3
        when {{ goals_for }} = {{ goals_against }} then 1
        when {{ goals_for }} < {{ goals_against }} then 0
        else 0
    end
{% endmacro %}
