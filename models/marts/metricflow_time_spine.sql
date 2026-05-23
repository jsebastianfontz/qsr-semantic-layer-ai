{{
    config(
        materialized = 'table'
    )
}}

with spine as (
    {{ dbt_utils.date_spine(
        datepart   = "day",
        start_date = "cast('2020-01-01' as date)",
        end_date   = "cast('2025-01-01' as date)"
    ) }}
)

select cast(date_day as date) as date_day
from spine
