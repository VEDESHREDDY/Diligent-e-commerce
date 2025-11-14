WITH customer_activity AS (
    SELECT
        u.user_id,
        u.first_name || ' ' || u.last_name AS customer_name,
        strftime('%Y-%m', u.signup_date) AS cohort_month,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(COALESCE(o.total_amount, 0)) AS total_revenue,
        AVG(COALESCE(o.total_amount, 0)) AS avg_order_value
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.user_id
    GROUP BY u.user_id
),
payment_health AS (
    SELECT
        o.user_id,
        AVG(CASE WHEN p.status = 'succeeded' THEN 1.0 ELSE 0.0 END) AS payment_success_ratio
    FROM orders o
    LEFT JOIN payments p ON p.order_id = o.order_id
    GROUP BY o.user_id
),
order_frequency AS (
    SELECT
        u.user_id,
        CASE
            WHEN COUNT(DISTINCT strftime('%Y-%m', o.order_date)) = 0 THEN 0
            ELSE CAST(COUNT(DISTINCT o.order_id) AS REAL) /
                 COUNT(DISTINCT strftime('%Y-%m', o.order_date))
        END AS monthly_frequency
    FROM users u
    LEFT JOIN orders o ON o.user_id = u.user_id
    GROUP BY u.user_id
)
SELECT
    ca.cohort_month,
    COUNT(*) AS customers,
    ROUND(SUM(ca.total_revenue), 2) AS total_revenue,
    ROUND(AVG(ca.avg_order_value), 2) AS avg_order_value,
    ROUND(AVG(ph.payment_success_ratio), 3) AS successful_payment_ratio,
    ROUND(AVG(ofq.monthly_frequency), 2) AS order_frequency
FROM customer_activity ca
LEFT JOIN payment_health ph ON ph.user_id = ca.user_id
LEFT JOIN order_frequency ofq ON ofq.user_id = ca.user_id
GROUP BY ca.cohort_month
ORDER BY ca.cohort_month;

