# CPG Revenue Growth & Trade Promotion Diagnostic

An independent commercial analytics case study focused on **revenue planning, pricing, trade promotion performance, ROTI, customer/channel/SKU performance, and pricing scenario modelling**.

> **Data transparency:** All commercial data in this project is simulated. The dataset contains 56,160 weekly customer × region × SKU observations across 18 SKUs, 10 customers, 5 channels and 6 Canadian regions. Selected promotional patterns are intentionally injected to test the analytical workflow. No real retailer, CPG, NielsenIQ, Circana, LDIA or Scintilla data is used.

## Live case study

The root `index.html` is GitHub Pages-ready. After Pages is enabled from the `main` branch, the case study will be available at `https://felipervm.github.io/cpg-revenue-growth-analytics/`.

## Business questions

1. Why did actual revenue miss the annual plan?
2. Which promotions create profitable incremental growth versus only volume?
3. Where is there potential pricing headroom?
4. Which customers, channels and SKUs require commercial action?
5. How should trade spend be reallocated?

## Headline findings

- Revenue plan: **$26.88M**
- Actual revenue: **$25.87M**
- Gap: **$1.02M / 3.8% below plan**
- Rate / price dilution explains approximately **$1.00M** of the portfolio variance
- Example deep-discount event: **+123% unit lift but only 0.14x ROTI**
- Example higher-value event: **+89% lift and 1.82x ROTI**
- Customer D: approximately **8.0% below revenue plan**
- PR-CHO-4 pricing model: a **+3%** scenario raises modeled gross profit while keeping price close to the simulated competitor benchmark

## Repository structure

- `index.html` — editorial interactive case study
- `data/simulated_cpg_commercial_data.csv.gz` — full synthetic dataset, generated locally and intentionally excluded from Git
- `data/portfolio_summary.csv` — portfolio KPIs
- `data/revenue_variance_decomposition.csv` — volume / mix / rate decomposition
- `data/promotion_event_performance.csv` — event-level lift, trade spend, ROI and ROTI, generated locally and intentionally excluded from Git
- `data/promotion_traps.csv` — selected high-lift, low-return events
- `data/high_value_promotion_events.csv` — selected higher-return events
- `data/channel_performance.csv` — channel revenue and contribution view
- `data/customer_performance.csv` — customer performance view
- `data/sku_performance.csv` — SKU pricing, competitive and contribution metrics
- `data/pricing_scenarios_pr_cho_4.csv` — price / volume / margin sensitivity
- `scripts/generate_simulated_data.py` — deterministic synthetic-data generator
- `scripts/analyze_commercial_performance.py` — analysis pipeline
- `sql/commercial_analysis.sql` — SQL versions of core analyses
- `CPG_Revenue_Growth_Pricing_Model.xlsx` — editable Excel pricing + promotion model
- `powerbi_ready/` — lightweight aggregate datasets plus build guide; event-level file is generated locally

## Reproduce

```bash
pip install -r requirements.txt
python scripts/generate_simulated_data.py
python scripts/analyze_commercial_performance.py
```

## Metric definitions

**Revenue variance decomposition**
- Volume effect: change in total units at planned average price
- Mix effect: change in SKU/customer mix valued at planned prices
- Rate / price effect: actual unit volume multiplied by the difference between actual and planned net price

**ROTI**
- `incremental gross profit / trade spend`

**ROI after trade spend**
- `(incremental gross profit - trade spend) / trade spend`

**Promotional lift**
- `(actual units / baseline units) - 1`

These definitions are explicit because commercial organizations can use different internal conventions.

## Pricing-model limitation

The pricing scenario uses an **assumed elasticity of -0.9** for PR-CHO-4. This is a transparent modelling assumption used to demonstrate scenario analysis; it is not presented as a statistically estimated causal elasticity. In production, the assumption should be replaced or validated using observed price-response data.

## Skills demonstrated

**Commercial Analytics · Revenue Growth Management · Pricing · Trade Promotion Analytics · ROI / ROTI · Scenario Modelling · Customer / Channel / SKU Analysis · Excel · SQL · Python · Pandas · Data Visualization · Git/GitHub · Data Quality**

## Author

**Felipe Mattos**

Independent portfolio project · Simulated data · Not affiliated with any retailer or CPG company.