{#
  Season type from the NBA's id encoding, in one place so the fact and dimension models
  cannot drift apart. The old `season_id like '%420%'` rule labelled everything non-playoff
  as regular season, which mislabels preseason once it is collected.

    season_id  1xxxx preseason  2xxxx regular  4xxxx playoffs  5xxxx play-in
    game_id    001.. preseason  002.. regular  004.. playoffs  005.. play-in

  Unrecognised values become 'other' so they fall out of the models' filters rather than
  quietly joining the regular season.
#}

{% macro season_type_from_season_id(column) %}
    case substring(cast({{ column }} as varchar), 1, 1)
        when '1' then 'preseason'
        when '2' then 'regular'
        when '4' then 'playoffs'
        when '5' then 'play_in'
        when '3' then 'all_star'
        else 'other'
    end
{% endmacro %}

{% macro season_type_from_game_id(column) %}
    case substring(cast({{ column }} as varchar), 1, 3)
        when '001' then 'preseason'
        when '002' then 'regular'
        when '004' then 'playoffs'
        when '005' then 'play_in'
        when '003' then 'all_star'
        else 'other'
    end
{% endmacro %}
