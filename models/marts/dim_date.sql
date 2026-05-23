-- Spine covering Jan 2023 – Dec 2024 plus the metricflow time spine anchor
with spine as (
    {{ dbt_utils.date_spine(
        datepart   = "day",
        start_date = "cast('2023-01-01' as date)",
        end_date   = "cast('2025-01-01' as date)"
    ) }}
),

final as (
    select
        cast(date_day as date)                        as date_day,
        year(date_day)                                as year,
        quarter(date_day)                             as quarter,
        month(date_day)                               as month,
        day(date_day)                                 as day_of_month,
        dayofweek(date_day)                           as day_of_week,   -- 0=Sun in DuckDB
        strftime(date_day, '%A')                      as day_name,
        strftime(date_day, '%B')                      as month_name,
        date_trunc('week',  date_day)::date           as week_start,
        date_trunc('month', date_day)::date           as month_start,
        date_trunc('quarter', date_day)::date         as quarter_start,
        date_trunc('year',  date_day)::date           as year_start,

        -- convenience flags
        case when dayofweek(date_day) in (0, 6) then true else false end as is_weekend,

        -- holiday flags (US)
        case
            when month(date_day) = 1  and day(date_day) = 1  then 'New Year''s Day'
            when month(date_day) = 7  and day(date_day) = 4  then 'Independence Day'
            when month(date_day) = 12 and day(date_day) = 25 then 'Christmas Day'
            when month(date_day) = 12 and day(date_day) = 24 then 'Christmas Eve'
            else null
        end as us_holiday,

        -- seasonal period
        case
            when month(date_day) in (11, 12) then 'Holiday'
            when month(date_day) in (6, 7, 8) then 'Summer'
            else 'Regular'
        end as season
    from spine
)

select * from final
