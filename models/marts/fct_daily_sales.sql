with sales as (
    select * from {{ ref('stg_daily_sales') }}
),

stores as (
    select * from {{ ref('dim_store') }}
),

dates as (
    select * from {{ ref('dim_date') }}
),

targets as (
    select * from {{ ref('stg_monthly_targets') }}
),

joined as (
    select
        -- keys
        s.store_id,
        s.sale_date,

        -- store attributes
        st.region,
        st.city,
        st.state,
        st.open_date,
        st.is_same_store_eligible,
        st.open_year,

        -- date attributes
        d.year,
        d.quarter,
        d.month,
        d.month_name,
        d.day_name,
        d.is_weekend,
        d.season,
        d.us_holiday,
        d.week_start,
        d.month_start,
        d.quarter_start,

        -- sales metrics
        s.gross_sales,
        s.net_sales,
        s.digital_sales,
        s.in_store_sales,
        s.transaction_count,

        -- derived
        s.gross_sales - s.net_sales                     as discount_amount,
        s.digital_sales / nullif(s.net_sales, 0)        as digital_mix_pct,
        s.net_sales     / nullif(s.transaction_count, 0) as avg_ticket_value,

        -- monthly target (prorated to day: target / days_in_month)
        t.sales_target / day(last_day(s.sale_date))     as daily_target

    from sales s
    left join stores   st on s.store_id  = st.store_id
    left join dates     d on s.sale_date = d.date_day
    left join targets   t
        on s.store_id   = t.store_id
        and year(s.sale_date)  = t.target_year
        and month(s.sale_date) = t.target_month
)

select * from joined
