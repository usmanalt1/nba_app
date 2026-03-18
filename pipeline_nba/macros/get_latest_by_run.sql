{% macro get_latest_by_run_timestamp(table_name, partition_key) %}
(
    select * from (
        select *,
               row_number() over (partition by {{ partition_key }} order by run_timestamp desc) as rn
        from {{ source('nba_dataset', table_name) }}
    ) as ranked_rows
    where rn = 1
)

{% endmacro %}