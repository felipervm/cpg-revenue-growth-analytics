-- CPG Revenue Growth & Trade Promotion Diagnostic
-- All source data is simulated.

-- 1) Revenue plan performance
SELECT
    SUM(plan_revenue) AS plan_revenue,
    SUM(actual_revenue) AS actual_revenue,
    SUM(actual_revenue) - SUM(plan_revenue) AS revenue_gap,
    (SUM(actual_revenue) / NULLIF(SUM(plan_revenue), 0) - 1) * 100 AS revenue_gap_pct
FROM simulated_cpg_commercial_data;

-- 2) Customer performance
SELECT
    customer,
    channel,
    SUM(plan_revenue) AS plan_revenue,
    SUM(actual_revenue) AS actual_revenue,
    SUM(actual_revenue) - SUM(plan_revenue) AS revenue_gap,
    (SUM(actual_revenue) / NULLIF(SUM(plan_revenue), 0) - 1) * 100 AS revenue_gap_pct,
    SUM(contribution_after_trade) / NULLIF(SUM(actual_revenue), 0) * 100 AS contribution_margin_pct
FROM simulated_cpg_commercial_data
GROUP BY customer, channel
ORDER BY revenue_gap_pct;

-- 3) Promotion event economics
WITH events AS (
    SELECT
        event_group,
        week,
        customer,
        channel,
        category,
        sku,
        product,
        promo_type,
        SUM(baseline_units) AS baseline_units,
        SUM(actual_units) AS actual_units,
        SUM(trade_spend) AS trade_spend,
        SUM(incremental_gross_profit) AS incremental_gp
    FROM simulated_cpg_commercial_data
    WHERE promo_flag = 1
    GROUP BY 1,2,3,4,5,6,7,8
)
SELECT
    *,
    (actual_units / NULLIF(baseline_units, 0) - 1) * 100 AS lift_pct,
    incremental_gp / NULLIF(trade_spend, 0) AS roti,
    (incremental_gp - trade_spend) / NULLIF(trade_spend, 0) AS roi_after_trade
FROM events
ORDER BY trade_spend DESC;

-- 4) Promotion traps: strong volume, weak payback
WITH event_metrics AS (
    SELECT
        event_group,
        customer,
        sku,
        promo_type,
        SUM(baseline_units) AS baseline_units,
        SUM(actual_units) AS actual_units,
        SUM(trade_spend) AS trade_spend,
        SUM(incremental_gross_profit) AS incremental_gp
    FROM simulated_cpg_commercial_data
    WHERE promo_flag = 1
    GROUP BY 1,2,3,4
)
SELECT
    *,
    (actual_units / NULLIF(baseline_units, 0) - 1) * 100 AS lift_pct,
    incremental_gp / NULLIF(trade_spend, 0) AS roti
FROM event_metrics
WHERE actual_units > baseline_units * 1.40
  AND incremental_gp / NULLIF(trade_spend, 0) < 1.0
ORDER BY trade_spend DESC;

-- 5) SKU pricing / competitive view
SELECT
    category,
    sku,
    product,
    SUM(actual_revenue) AS actual_revenue,
    SUM(contribution_after_trade) AS contribution_after_trade,
    AVG(actual_net_price) AS avg_net_price,
    AVG(competitor_price) AS avg_competitor_price,
    (AVG(competitor_price) / NULLIF(AVG(actual_net_price), 0) - 1) * 100 AS competitor_gap_pct
FROM simulated_cpg_commercial_data
GROUP BY category, sku, product
ORDER BY actual_revenue DESC;

-- 6) Channel performance
SELECT
    channel,
    SUM(plan_revenue) AS plan_revenue,
    SUM(actual_revenue) AS actual_revenue,
    (SUM(actual_revenue) / NULLIF(SUM(plan_revenue),0) - 1) * 100 AS revenue_gap_pct,
    SUM(trade_spend) AS trade_spend,
    SUM(contribution_after_trade) / NULLIF(SUM(actual_revenue),0) * 100 AS contribution_margin_pct
FROM simulated_cpg_commercial_data
GROUP BY channel
ORDER BY revenue_gap_pct;
