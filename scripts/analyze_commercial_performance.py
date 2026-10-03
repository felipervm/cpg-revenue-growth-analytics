from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "simulated_cpg_commercial_data.csv.gz"

df = pd.read_csv(RAW)

plan_revenue = df["plan_revenue"].sum()
actual_revenue = df["actual_revenue"].sum()
plan_units = df["plan_units"].sum()
actual_units = df["actual_units"].sum()

plan_avg_price = plan_revenue / plan_units
actual_mix_plan_price = (df["actual_units"]*df["plan_net_price"]).sum()/actual_units
volume_effect = (actual_units-plan_units)*plan_avg_price
mix_effect = actual_units*(actual_mix_plan_price-plan_avg_price)
rate_effect = (df["actual_units"]*(df["actual_net_price"]-df["plan_net_price"])).sum()

portfolio = pd.DataFrame([{
    "plan_revenue": plan_revenue,
    "actual_revenue": actual_revenue,
    "revenue_gap": actual_revenue-plan_revenue,
    "revenue_gap_pct": (actual_revenue/plan_revenue-1)*100,
    "plan_units": plan_units,
    "actual_units": actual_units,
    "trade_spend": df["trade_spend"].sum(),
    "gross_profit": df["gross_profit"].sum(),
    "contribution_after_trade": df["contribution_after_trade"].sum(),
    "gross_margin_pct": df["gross_profit"].sum()/actual_revenue*100,
    "contribution_margin_pct": df["contribution_after_trade"].sum()/actual_revenue*100,
}])
portfolio.to_csv(DATA/"portfolio_summary.csv", index=False)

pd.DataFrame({
    "driver":["Volume","Mix","Rate / Price"],
    "revenue_variance":[volume_effect,mix_effect,rate_effect]
}).to_csv(DATA/"revenue_variance_decomposition.csv", index=False)

def perf(group_cols, output):
    d = df.groupby(group_cols, as_index=False).agg(
        plan_revenue=("plan_revenue","sum"),
        actual_revenue=("actual_revenue","sum"),
        gross_profit=("gross_profit","sum"),
        contribution=("contribution_after_trade","sum"),
        trade_spend=("trade_spend","sum"),
        actual_units=("actual_units","sum"),
    )
    d["revenue_gap"] = d["actual_revenue"]-d["plan_revenue"]
    d["revenue_gap_pct"] = (d["actual_revenue"]/d["plan_revenue"]-1)*100
    d["contribution_margin_pct"] = d["contribution"]/d["actual_revenue"]*100
    d.to_csv(DATA/output, index=False)
    return d

perf(["channel"], "channel_performance.csv")
perf(["customer","channel"], "customer_performance.csv")

sku = df.groupby(["category","sku","product"],as_index=False).agg(
    plan_revenue=("plan_revenue","sum"),
    actual_revenue=("actual_revenue","sum"),
    gross_profit=("gross_profit","sum"),
    contribution=("contribution_after_trade","sum"),
    trade_spend=("trade_spend","sum"),
    actual_units=("actual_units","sum"),
    avg_net_price=("actual_net_price","mean"),
    avg_competitor_price=("competitor_price","mean")
)
sku["revenue_gap"] = sku["actual_revenue"]-sku["plan_revenue"]
sku["revenue_gap_pct"] = (sku["actual_revenue"]/sku["plan_revenue"]-1)*100
sku["contribution_margin_pct"] = sku["contribution"]/sku["actual_revenue"]*100
sku["competitor_gap_pct"] = (sku["avg_competitor_price"]/sku["avg_net_price"]-1)*100
sku.to_csv(DATA/"sku_performance.csv", index=False)

promo = df[df["promo_flag"]==1].copy()
event = promo.groupby(
    ["event_group","week","customer","channel","category","sku","product","promo_type"],
    as_index=False
).agg(
    baseline_units=("baseline_units","sum"),
    actual_units=("actual_units","sum"),
    trade_spend=("trade_spend","sum"),
    actual_revenue=("actual_revenue","sum"),
    gross_profit=("gross_profit","sum"),
    contribution=("contribution_after_trade","sum"),
    incremental_gp=("incremental_gross_profit","sum")
)
event["lift_pct"] = (event["actual_units"]/event["baseline_units"]-1)*100
event["roti"] = event["incremental_gp"]/event["trade_spend"]
event["roi"] = (event["incremental_gp"]-event["trade_spend"])/event["trade_spend"]
event["value_flag"] = np.select(
    [event["roti"]>=1.5,event["roti"]>=1.0,event["roti"]<1.0],
    ["Scale / Protect","Review","Value-destructive"], default="Review"
)
event.to_csv(DATA/"promotion_event_performance.csv", index=False)

ptype = event.groupby("promo_type",as_index=False).agg(
    events=("event_group","count"),
    baseline_units=("baseline_units","sum"),
    actual_units=("actual_units","sum"),
    trade_spend=("trade_spend","sum"),
    incremental_gp=("incremental_gp","sum"),
    actual_revenue=("actual_revenue","sum")
)
ptype["lift_pct"] = (ptype["actual_units"]/ptype["baseline_units"]-1)*100
ptype["roti"] = ptype["incremental_gp"]/ptype["trade_spend"]
ptype["roi"] = (ptype["incremental_gp"]-ptype["trade_spend"])/ptype["trade_spend"]
ptype.to_csv(DATA/"promotion_type_summary.csv", index=False)

event[event["roti"]>=1.2].sort_values(["trade_spend","roti"],ascending=[False,False]).head(20).to_csv(
    DATA/"high_value_promotion_events.csv", index=False
)
event[(event["roti"]<1)&(event["lift_pct"]>40)].sort_values("trade_spend",ascending=False).head(20).to_csv(
    DATA/"promotion_traps.csv", index=False
)

# Pricing scenario: PR-CHO-4. Elasticity is a transparent modelling assumption, not an observed causal estimate.
s = df[(df["sku"]=="PR-CHO-4") & (df["promo_flag"]==0)].copy()
base_units = s["actual_units"].sum()
base_price = np.average(s["actual_net_price"], weights=np.maximum(s["actual_units"],1))
competitor = np.average(s["competitor_price"], weights=np.maximum(s["actual_units"],1))
cogs = s["cogs_per_unit"].iloc[0]
elasticity = -0.9

rows = []
for price_change in [-0.03,0,0.02,0.03,0.05]:
    scenario_price = base_price*(1+price_change)
    expected_units = base_units*(1+elasticity*price_change)
    revenue = scenario_price*expected_units
    gp = (scenario_price-cogs)*expected_units
    rows.append({
        "price_change_pct":price_change,
        "scenario_price":scenario_price,
        "expected_units":expected_units,
        "revenue":revenue,
        "gross_profit":gp,
        "gross_margin_pct":gp/revenue*100,
        "price_vs_competitor_pct":scenario_price/competitor-1
    })

pd.DataFrame(rows).to_csv(DATA/"pricing_scenarios_pr_cho_4.csv", index=False)
print("Analysis outputs refreshed.")
