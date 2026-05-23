import csv
import random
import math
from datetime import date, timedelta

random.seed(42)

REGIONS = {
    "Northeast": ["New York", "Boston", "Philadelphia", "Albany", "Hartford",
                  "Providence", "Newark", "Buffalo", "Rochester", "Syracuse",
                  "Trenton", "Bridgeport", "New Haven"],
    "Southeast": ["Atlanta", "Miami", "Charlotte", "Orlando", "Tampa",
                  "Nashville", "Richmond", "Raleigh", "Jacksonville", "Birmingham",
                  "Savannah", "Greenville", "Huntsville"],
    "West":      ["Los Angeles", "Seattle", "Phoenix", "Denver", "Portland",
                  "San Diego", "Las Vegas", "Salt Lake City", "Tucson", "Spokane",
                  "Sacramento", "Albuquerque", "Boise"],
    "Midwest":   ["Chicago", "Detroit", "Columbus", "Indianapolis", "Milwaukee",
                  "Cleveland", "Kansas City", "Minneapolis", "St. Louis", "Cincinnati",
                  "Omaha", "Grand Rapids", "Akron"],
}

REGION_STATE = {
    "New York": "NY", "Boston": "MA", "Philadelphia": "PA", "Albany": "NY",
    "Hartford": "CT", "Providence": "RI", "Newark": "NJ", "Buffalo": "NY",
    "Rochester": "NY", "Syracuse": "NY", "Trenton": "NJ", "Bridgeport": "CT",
    "New Haven": "CT",
    "Atlanta": "GA", "Miami": "FL", "Charlotte": "NC", "Orlando": "FL",
    "Tampa": "FL", "Nashville": "TN", "Richmond": "VA", "Raleigh": "NC",
    "Jacksonville": "FL", "Birmingham": "AL", "Savannah": "GA",
    "Greenville": "SC", "Huntsville": "AL",
    "Los Angeles": "CA", "Seattle": "WA", "Phoenix": "AZ", "Denver": "CO",
    "Portland": "OR", "San Diego": "CA", "Las Vegas": "NV",
    "Salt Lake City": "UT", "Tucson": "AZ", "Spokane": "WA",
    "Sacramento": "CA", "Albuquerque": "NM", "Boise": "ID",
    "Chicago": "IL", "Detroit": "MI", "Columbus": "OH", "Indianapolis": "IN",
    "Milwaukee": "WI", "Cleveland": "OH", "Kansas City": "MO",
    "Minneapolis": "MN", "St. Louis": "MO", "Cincinnati": "OH",
    "Omaha": "NE", "Grand Rapids": "MI", "Akron": "OH",
}

REGION_BASE_MULTIPLIER = {
    "Northeast": 1.15,
    "Southeast": 0.95,
    "West": 1.10,
    "Midwest": 1.00,
}

stores = []
store_id = 1
open_dates = {}

all_cities = []
for region, cities in REGIONS.items():
    for city in cities:
        all_cities.append((region, city))

random.shuffle(all_cities)
selected = all_cities[:50]

for i, (region, city) in enumerate(selected):
    sid = f"S{store_id:03d}"
    open_year = random.randint(2020, 2022)
    open_month = random.randint(1, 12)
    open_day = random.randint(1, 28)
    od = date(open_year, open_month, open_day)
    open_dates[sid] = od
    stores.append({
        "store_id": sid,
        "store_name": f"QSR {city} {store_id}",
        "city": city,
        "state": REGION_STATE[city],
        "region": region,
        "open_date": od.isoformat(),
    })
    store_id += 1

with open("seeds/stores.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["store_id","store_name","city","state","region","open_date"])
    w.writeheader()
    w.writerows(stores)

print(f"stores.csv: {len(stores)} rows")

# Base daily net sales per store: $8,000-$14,000
store_base = {s["store_id"]: random.uniform(8000, 14000) for s in stores}
store_region = {s["store_id"]: s["region"] for s in stores}

def day_multiplier(d: date) -> float:
    # Weekend peak
    dow = d.weekday()  # 0=Mon, 6=Sun
    if dow == 5:   # Saturday
        wk = 1.22
    elif dow == 6:  # Sunday
        wk = 1.18
    elif dow == 4:  # Friday
        wk = 1.10
    else:
        wk = 1.0

    # Monthly seasonality
    month_factor = {
        1: 0.88, 2: 0.90, 3: 0.95, 4: 0.98, 5: 1.00,
        6: 1.02, 7: 1.03, 8: 1.02, 9: 0.97, 10: 0.98,
        11: 1.12, 12: 1.20,
    }
    mo = month_factor[d.month]

    # Holiday bumps
    holiday_boost = 0.0
    # Thanksgiving week (last Thu of November)
    if d.month == 11 and d.weekday() == 3 and d.day >= 22:
        holiday_boost = 0.30
    # Christmas Eve/Day
    if d.month == 12 and d.day in (24, 25):
        holiday_boost = 0.35
    # New Year's
    if d.month == 1 and d.day == 1:
        holiday_boost = 0.20
    # July 4
    if d.month == 7 and d.day == 4:
        holiday_boost = 0.15
    # Labor Day (first Mon Sep)
    if d.month == 9 and d.weekday() == 0 and d.day <= 7:
        holiday_boost = 0.12
    # Memorial Day (last Mon May)
    if d.month == 5 and d.weekday() == 0 and d.day >= 25:
        holiday_boost = 0.12

    return wk * mo * (1 + holiday_boost)

daily_rows = []
start = date(2023, 1, 1)
end = date(2024, 12, 31)
d = start
while d <= end:
    for s in stores:
        sid = s["store_id"]
        base = store_base[sid]
        reg_mult = REGION_BASE_MULTIPLIER[store_region[sid]]
        dm = day_multiplier(d)
        noise = random.uniform(0.93, 1.07)

        gross = base * reg_mult * dm * noise
        net = gross * random.uniform(0.91, 0.94)  # ~8-9% discounts/refunds

        # Digital mix: 25-40%, higher on weekdays
        dow = d.weekday()
        digital_base = 0.32 if dow < 5 else 0.24
        digital_pct = digital_base + random.uniform(-0.05, 0.05)
        digital = net * digital_pct
        in_store = net - digital

        # Transaction count: avg ticket $12-16
        avg_ticket = random.uniform(12, 16)
        txn_count = max(1, int(net / avg_ticket + random.gauss(0, 5)))

        daily_rows.append({
            "store_id": sid,
            "sale_date": d.isoformat(),
            "gross_sales": round(gross, 2),
            "net_sales": round(net, 2),
            "digital_sales": round(digital, 2),
            "in_store_sales": round(in_store, 2),
            "transaction_count": txn_count,
        })
    d += timedelta(days=1)

with open("seeds/daily_sales.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["store_id","sale_date","gross_sales","net_sales",
                                       "digital_sales","in_store_sales","transaction_count"])
    w.writeheader()
    w.writerows(daily_rows)

print(f"daily_sales.csv: {len(daily_rows)} rows")

# Monthly targets: slightly above prior-year actuals or a growth-based target
from collections import defaultdict
monthly_actuals = defaultdict(float)
for row in daily_rows:
    d2 = date.fromisoformat(row["sale_date"])
    monthly_actuals[(row["store_id"], d2.year, d2.month)] += row["net_sales"]

target_rows = []
for s in stores:
    sid = s["store_id"]
    for year in [2023, 2024]:
        for month in range(1, 13):
            actual = monthly_actuals.get((sid, year, month), 0)
            # Target = actual * 1.03-1.08 (stretch goal)
            target = actual * random.uniform(1.03, 1.08)
            target_rows.append({
                "store_id": sid,
                "year": year,
                "month": month,
                "sales_target": round(target, 2),
            })

with open("seeds/monthly_targets.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["store_id","year","month","sales_target"])
    w.writeheader()
    w.writerows(target_rows)

print(f"monthly_targets.csv: {len(target_rows)} rows")
print("Done!")
