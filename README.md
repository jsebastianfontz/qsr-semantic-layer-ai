# QSR Analytics — dbt Core + DuckDB Portfolio Project

A fully self-contained analytics engineering portfolio project for a fictional Quick Service Restaurant (QSR) chain. It demonstrates a production-grade dbt project with synthetic data, a layered data model, MetricFlow semantic models, and four business metrics.

---

## Architecture

```
seeds/                  Raw synthetic CSVs (loaded once)
  stores.csv            50 stores across 4 US regions
  daily_sales.csv       ~36,550 rows — daily sales per store, Jan 2023–Dec 2024
  monthly_targets.csv   1,200 rows — monthly sales targets per store

models/
  staging/              1-to-1 with seeds; type casting, column renaming
  marts/                Dimensional model (dim_* + fct_*)
  semantic/             MetricFlow semantic model definition
  metrics/              MetricFlow metric definitions
```

### Lineage

```
stores.csv ──────────────────────────────┐
daily_sales.csv ──────────────────────────┼──► fct_daily_sales ──► metrics
monthly_targets.csv ─► stg_monthly_targets ┘
                          ▲
dim_store ◄── stg_stores ─┘
dim_date  ◄── dbt_utils.date_spine
metricflow_time_spine ◄── dbt_utils.date_spine
```

---

## Synthetic Data Design

| Feature | Detail |
|---------|--------|
| Stores | 50 locations, 4 regions (Northeast, Southeast, West, Midwest), opened 2020–2022 |
| Daily sales | Base $8k–$14k net/day; multiplied by region factor, day-of-week, month seasonality, noise |
| Weekend peak | +22% Saturday, +18% Sunday, +10% Friday |
| Holiday boosts | Thanksgiving +30%, Christmas +35%, July 4 +15%, Labor Day +12%, New Year's +20% |
| November–December | Month multipliers 1.12 and 1.20 above baseline |
| Regional variation | Northeast 1.15×, West 1.10×, Midwest 1.00×, Southeast 0.95× |
| Digital mix | ~24–32% of net sales (lower on weekends, ±5% noise) |
| Targets | Monthly target = actual × 1.03–1.08 (stretch goals) |

---

## Metrics

| Metric | Type | Formula |
|--------|------|---------|
| `total_net_sales` | simple | `SUM(net_sales)` |
| `same_store_sales_growth` | ratio | Current / Prior period net sales, same-store-eligible stores only (open ≥ 12 months before 2023-01-01) |
| `target_attainment` | ratio | `SUM(net_sales) / SUM(daily_target)` |
| `digital_channel_mix` | ratio | `SUM(digital_sales) / SUM(net_sales)` |

---

## Setup & Running

### Prerequisites

```bash
pip install dbt-duckdb dbt-utils
```

### 1. Install dbt packages

```bash
cd qsr_analytics
dbt deps
```

### 2. Load seed data

```bash
dbt seed
```

### 3. Run all models

```bash
dbt run
```

### 4. Run tests

```bash
dbt test
```

### 5. Generate docs

```bash
dbt docs generate
dbt docs serve
```

### 6. Query metrics via MetricFlow (dbt 1.6+)

```bash
dbt sl query --metrics total_net_sales --group-by metric_time__month
dbt sl query --metrics total_net_sales,digital_channel_mix --group-by metric_time__month,region
dbt sl query --metrics target_attainment --group-by metric_time__month,store_id
```

---

## Project Structure

```
qsr_analytics/
├── dbt_project.yml
├── profiles.yml               # DuckDB target (local file: qsr.duckdb)
├── packages.yml
├── generate_seeds.py          # Script that produced the CSV seeds
├── seeds/
│   ├── schema.yml
│   ├── stores.csv
│   ├── daily_sales.csv
│   └── monthly_targets.csv
├── models/
│   ├── staging/
│   │   ├── schema.yml
│   │   ├── stg_stores.sql
│   │   ├── stg_daily_sales.sql
│   │   └── stg_monthly_targets.sql
│   ├── marts/
│   │   ├── schema.yml
│   │   ├── dim_store.sql
│   │   ├── dim_date.sql
│   │   ├── fct_daily_sales.sql
│   │   └── metricflow_time_spine.sql
│   ├── semantic/
│   │   └── sem_store_sales.yml
│   └── metrics/
│       └── metrics.yml
└── README.md
```

---

## Key Design Decisions

- **DuckDB** — zero-infrastructure local analytics; ideal for portfolio/demo projects.
- **Layered architecture** — staging → marts separates raw cleaning from business logic.
- **`is_same_store_eligible`** — computed once in `dim_store`, propagated to the fact table and used in the same-store-sales-growth metric without needing a filter in SQL.
- **Prorated daily target** — `monthly_target / days_in_month` makes daily, weekly, and monthly aggregations naturally consistent.
- **MetricFlow** — metrics defined declaratively; consumers can slice by any dimension without writing SQL.
