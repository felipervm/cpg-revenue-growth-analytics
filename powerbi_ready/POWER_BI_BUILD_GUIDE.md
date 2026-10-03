# Power BI Build Guide

This folder contains aggregate, import-ready CSVs for a compact commercial analytics dashboard.

## Recommended pages

### 1. Executive Revenue Plan
Use:
- `portfolio_summary.csv`
- `revenue_variance_decomposition.csv`
- `channel_performance.csv`

Visuals:
- KPI cards: Plan Revenue, Actual Revenue, Gap %, Trade Spend, Contribution Margin
- Waterfall: Volume / Mix / Rate variance
- Channel revenue gap bar chart

### 2. Trade Promotion Performance
Use:
- `promotion_event_performance.csv`
- `promotion_type_summary.csv`

Visuals:
- Scatter: Lift % vs ROTI, bubble size = Trade Spend
- Promotion type summary
- Table with Customer, SKU, Lift, Spend, Incremental GP, ROTI, ROI
- Conditional formatting for ROTI < 1.0x

### 3. Customer & SKU Performance
Use:
- `customer_performance.csv`
- `sku_performance.csv`

Visuals:
- Customer revenue gap
- SKU contribution margin
- Net price vs competitor price
- Filters for channel, customer, category and SKU

### 4. Pricing Scenario
Use:
- `pricing_scenarios_pr_cho_4.csv`

Visuals:
- Clustered columns: Revenue and Gross Profit by price scenario
- Cards: Current Price, Competitor Price, +3% Scenario Gross Profit

## Transparency note
All data is simulated. The pricing elasticity is an explicit modelling assumption, not an observed causal estimate.
