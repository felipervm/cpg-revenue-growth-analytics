from pathlib import Path
import numpy as np
import pandas as pd

SEED = 73
OUT = Path(__file__).resolve().parents[1] / "data" / "simulated_cpg_commercial_data.csv.gz"
rng = np.random.default_rng(SEED)

weeks = pd.date_range("2026-01-05", periods=52, freq="W-MON")
customers = [
    ("Customer A","Grocery",1.20),("Customer B","Grocery",1.05),
    ("Customer C","Mass",1.30),("Customer D","Mass",0.95),
    ("Customer E","Club",0.85),("Customer F","Convenience",0.70),
    ("Customer G","Convenience",0.62),("Customer H","E-commerce",0.72),
    ("Customer I","Grocery",0.90),("Customer J","E-commerce",0.55),
]
regions = [("Ontario",1.0),("Quebec",0.78),("West",0.72),("Atlantic",0.40),("Prairies",0.52),("British Columbia",0.58)]

categories = {
    "Sparkling Water": [
        ("SW-LIME-8","Lime 8-pack",5.49,2.05,1.05),
        ("SW-BERRY-8","Berry 8-pack",5.69,2.10,0.98),
        ("SW-GRAPE-8","Grapefruit 8-pack",5.59,2.08,0.92),
        ("SW-LEMON-12","Lemon 12-pack",7.79,2.85,0.83),
    ],
    "Energy": [
        ("EN-CITRUS-4","Citrus 4-pack",9.99,4.05,0.78),
        ("EN-BERRY-4","Berry 4-pack",10.49,4.15,0.73),
        ("EN-CITRUS-12","Citrus 12-pack",25.99,10.20,0.56),
        ("EN-TROPIC-12","Tropical 12-pack",26.49,10.40,0.50),
    ],
    "Protein": [
        ("PR-VAN-4","Vanilla 4-pack",12.49,5.55,0.68),
        ("PR-CHO-4","Chocolate 4-pack",12.49,5.65,0.72),
        ("PR-COF-4","Coffee 4-pack",12.99,5.70,0.57),
        ("PR-VAN-12","Vanilla 12-pack",32.99,14.25,0.45),
    ],
    "Snack Bars": [
        ("SB-CHO-6","Chocolate 6-pack",6.99,2.95,0.88),
        ("SB-PNT-6","Peanut 6-pack",7.19,3.00,0.91),
        ("SB-BRY-6","Berry 6-pack",7.09,2.98,0.74),
        ("SB-MIX-18","Variety 18-pack",17.99,7.25,0.48),
    ],
    "Electrolytes": [
        ("EL-LEM-10","Lemon 10-pack",11.99,4.50,0.69),
        ("EL-BRY-10","Berry 10-pack",11.99,4.55,0.67),
    ],
}

sku_rows = []
for category, items in categories.items():
    for sku, product, regular_price, cogs, velocity in items:
        sku_rows.append((category, sku, product, regular_price, cogs, velocity))

promo_types = ["TPR 10%","TPR 15%","Feature + Display","Deep Discount"]
promo_disc = {"TPR 10%":0.10,"TPR 15%":0.15,"Feature + Display":0.18,"Deep Discount":0.28}
promo_lift = {"TPR 10%":0.15,"TPR 15%":0.26,"Feature + Display":0.42,"Deep Discount":0.68}
promo_trade_per_unit = {"TPR 10%":0.18,"TPR 15%":0.28,"Feature + Display":0.42,"Deep Discount":0.62}
promo_prop = {"Grocery":0.18,"Mass":0.20,"Club":0.11,"Convenience":0.10,"E-commerce":0.15}
cust_price_factor = {c: rng.uniform(0.965,1.01) for c,_,_ in customers}

rows = []
event_counter = 1

for week_num, week in enumerate(weeks, start=1):
    seasonal = 1 + 0.08*np.sin((week_num-8)/52*2*np.pi) + (0.07 if 22 <= week_num <= 35 else 0)
    for customer, channel, customer_factor in customers:
        for region, region_factor in regions:
            for category, sku, product, regular_price, cogs, velocity in sku_rows:
                demand = 92*customer_factor*region_factor*velocity*seasonal
                if category in ["Sparkling Water","Electrolytes"] and 20 <= week_num <= 35:
                    demand *= 1.15
                if category == "Snack Bars" and week_num in [35,36,37,38]:
                    demand *= 1.12

                baseline_units = max(5, int(rng.normal(demand, max(3,demand*0.10))))
                plan_units = max(5, int(baseline_units * rng.normal(1.035,0.025)))
                plan_units = int(np.ceil(plan_units * 1.027))
                plan_price = regular_price * cust_price_factor[customer]

                quarter_price = 1.0 + (0.007 if week_num >= 27 else 0) + (0.005 if week_num >= 40 else 0)
                regular_net = plan_price * quarter_price

                is_promo = rng.random() < promo_prop[channel]
                promo_type, discount, lift, event_id, fixed_fee = "", 0, 0, "", 0

                if is_promo:
                    promo_type = rng.choice(promo_types, p=[0.32,0.34,0.24,0.10])
                    discount = promo_disc[promo_type]
                    lift = promo_lift[promo_type]
                    event_id = f"EVT-{event_counter:05d}"
                    event_counter += 1
                    fixed_fee = {"TPR 10%":40,"TPR 15%":65,"Feature + Display":130,"Deep Discount":160}[promo_type]*region_factor

                # Intentionally injected "promotion trap":
                # deep discount on Energy Citrus 12-pack creates large lift but poor return on trade investment.
                trap = sku == "EN-CITRUS-12" and channel in ["Mass","Grocery"] and 27 <= week_num <= 39 and rng.random() < 0.45
                if trap:
                    is_promo, promo_type, discount, lift = True, "Deep Discount", 0.32, 0.88
                    event_id = f"TRAP-{event_counter:05d}"
                    event_counter += 1
                    fixed_fee = 240*region_factor

                # Intentionally injected efficient promotion to create a useful comparison.
                efficient = sku == "SW-LIME-8" and channel == "Grocery" and 10 <= week_num <= 42 and rng.random() < 0.25
                if efficient:
                    is_promo, promo_type, discount, lift = True, "Feature + Display", 0.14, 0.52
                    event_id = f"WIN-{event_counter:05d}"
                    event_counter += 1
                    fixed_fee = 70*region_factor

                actual_price = regular_net * (1-discount)
                competitor_price = regular_price*rng.normal(1.015,0.035)

                elasticity = {"Sparkling Water":-1.4,"Energy":-1.2,"Protein":-0.9,"Snack Bars":-1.3,"Electrolytes":-1.1}[category]
                price_change = (actual_price-plan_price)/plan_price
                competitor_gap = (competitor_price-actual_price)/actual_price
                unit_multiplier = 1 + elasticity*price_change + 0.16*competitor_gap + lift
                if 14 <= week_num <= 26:
                    unit_multiplier *= 0.965
                if customer == "Customer D":
                    unit_multiplier *= 0.94

                actual_units = max(0, int(baseline_units*unit_multiplier*rng.normal(1,0.06)))
                revenue = actual_units*actual_price
                gross_profit = (actual_price-cogs)*actual_units

                trade_spend = 0
                if is_promo:
                    per_unit = promo_trade_per_unit.get(promo_type,0.3)
                    if trap:
                        per_unit = 1.85
                    if efficient:
                        per_unit = 0.22
                    trade_spend = actual_units*per_unit + fixed_fee

                contribution = gross_profit-trade_spend
                baseline_gp = (regular_net-cogs)*baseline_units
                incremental_gp = gross_profit-baseline_gp
                roti = incremental_gp/trade_spend if trade_spend > 0 else np.nan
                roi = (incremental_gp-trade_spend)/trade_spend if trade_spend > 0 else np.nan

                rows.append({
                    "week": week.date().isoformat(),
                    "week_num": week_num,
                    "customer": customer,
                    "channel": channel,
                    "region": region,
                    "category": category,
                    "sku": sku,
                    "product": product,
                    "plan_units": plan_units,
                    "baseline_units": baseline_units,
                    "actual_units": actual_units,
                    "plan_net_price": round(plan_price,2),
                    "regular_net_price": round(regular_net,2),
                    "actual_net_price": round(actual_price,2),
                    "competitor_price": round(competitor_price,2),
                    "cogs_per_unit": round(cogs,2),
                    "promo_flag": int(is_promo),
                    "promo_type": promo_type,
                    "event_id": event_id,
                    "discount_pct": round(discount,4),
                    "trade_spend": round(trade_spend,2),
                    "plan_revenue": round(plan_units*plan_price,2),
                    "actual_revenue": round(revenue,2),
                    "gross_profit": round(gross_profit,2),
                    "contribution_after_trade": round(contribution,2),
                    "incremental_units": actual_units-baseline_units,
                    "incremental_gross_profit": round(incremental_gp,2),
                    "roti": round(roti,4) if not np.isnan(roti) else np.nan,
                    "roi": round(roi,4) if not np.isnan(roi) else np.nan,
                })

df = pd.DataFrame(rows)
df["event_group"] = np.where(
    df["promo_flag"].eq(1),
    df["week"].astype(str)+"_"+df["customer"]+"_"+df["sku"]+"_"+df["promo_type"],
    ""
)

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False, compression="gzip")
print(f"Wrote {len(df):,} simulated commercial rows to {OUT}")
