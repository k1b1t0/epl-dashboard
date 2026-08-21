{% macro get_match_result(goals_for, goals_against) %}
    case 
        when {{ goals_for }} > {{ goals_against }} then 'WIN'
        when {{ goals_for }} = {{ goals_against }} then 'DRAW'
        when {{ goals_for }} < {{ goals_against }} then 'LOST'
        else null
    end
{% endmacro %}
