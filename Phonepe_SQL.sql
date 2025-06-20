CREATE DATABASE phonepe_transaction;

use phonepe_transaction;

#Decoding Transaction Dynamics on PhonePe

WITH state_trend AS (SELECT state, year, quarter, transaction_type, 
SUM(transaction_count) AS total_transactions,SUM(transaction_amount) AS total_amount,
LAG(SUM(transaction_amount)) OVER (PARTITION BY state, transaction_type ORDER BY year, quarter) AS prev_amount
FROM agg_trans GROUP BY state, year, quarter, transaction_type),
growth_analysis AS (SELECT state, year, quarter, transaction_type, total_transactions, total_amount,
(total_amount - prev_amount) / NULLIF(prev_amount, 0) * 100 AS growth_percentage
FROM state_trend), category_trend AS (SELECT transaction_type, year, quarter, 
SUM(transaction_count) AS total_transactions, SUM(transaction_amount) AS total_amount,
LAG(SUM(transaction_amount)) OVER (PARTITION BY transaction_type ORDER BY year, quarter) AS prev_amount
FROM agg_trans GROUP BY transaction_type, year, quarter), category_growth AS (SELECT 
transaction_type, year, quarter, total_transactions, total_amount,
(total_amount - prev_amount) / NULLIF(prev_amount, 0) * 100 AS growth_percentage
FROM category_trend), final_trends AS (SELECT state, transaction_type, year, quarter, total_transactions, total_amount, growth_percentage,
CASE WHEN growth_percentage > 5 THEN 'Growing'WHEN growth_percentage BETWEEN -5 AND 5 THEN 'Stable'
ELSE 'Declining' END AS trend_status FROM growth_analysis)
SELECT * FROM final_trends ORDER BY year DESC, quarter DESC, growth_percentage DESC;

# Device Dominance and User Engagement Analysis

WITH brand_engagement AS (SELECT state, brand, year, quarter, 
SUM(registered_users) AS total_registered_users, SUM(app_opens) AS total_app_opens,
(SUM(app_opens) / NULLIF(SUM(registered_users), 0)) * 100 AS engagement_rate,
LAG(SUM(app_opens)) OVER (PARTITION BY brand ORDER BY year, quarter) AS prev_app_opens
FROM agg_users WHERE brand IS NOT NULL AND brand <> 'Unknown'  GROUP BY state, brand, year, quarter),
growth_analysis AS (SELECT *, ((total_app_opens - prev_app_opens) / NULLIF(prev_app_opens, 0)) * 100 
AS growth_percentage FROM brand_engagement) SELECT * FROM growth_analysis
ORDER BY year DESC, quarter DESC, engagement_rate DESC;

#Insurance Penetration and Growth Potential Analysis

WITH insurance_trend AS (SELECT state, year, quarter, insurance_type, 
SUM(insurance_count) AS total_policies, SUM(insurance_amount) AS total_value,
LAG(SUM(insurance_amount)) OVER (PARTITION BY state, insurance_type ORDER BY year, quarter) AS prev_value
FROM map_insur GROUP BY state, year, quarter, insurance_type), 
penetration_analysis AS (SELECT mi.state, mi.year, mi.quarter, mi.insurance_type, 
(SUM(mi.insurance_count) * 100.0) / NULLIF(SUM(at.transaction_count), 0) AS penetration_rate
FROM map_insur mi JOIN agg_trans at USING (state, year, quarter)
GROUP BY mi.state, mi.year, mi.quarter, mi.insurance_type)
SELECT it.state, it.year, it.quarter, it.insurance_type, 
it.total_policies, it.total_value, (it.total_value - it.prev_value) / NULLIF(it.prev_value, 0) * 100 
AS growth_percentage, pa.penetration_rate FROM insurance_trend it JOIN penetration_analysis pa 
USING (state, year, quarter, insurance_type) ORDER BY growth_percentage DESC, penetration_rate DESC;

#Transaction Analysis for Market Expansion

WITH state_growth AS (SELECT state, year, quarter
, SUM(transaction_count) AS total_transactions, 
SUM(transaction_amount) AS total_amount,LAG(SUM(transaction_amount)) 
OVER (PARTITION BY state ORDER BY year, quarter) AS prev_amount FROM agg_trans
GROUP BY state, year, quarter) SELECT state, SUM(total_transactions) AS total_transactions,
SUM(total_amount) AS total_transaction_amount,
ROUND(AVG((total_amount - prev_amount) / NULLIF(prev_amount, 0) * 100), 2) AS avg_growth_rate 
FROM state_growth GROUP BY state ORDER BY avg_growth_rate DESC, total_transaction_amount DESC;

#Transaction Analysis Across States and Districts

WITH state_transaction AS (SELECT state, SUM(transaction_count) AS total_transactions, 
SUM(transaction_amount) AS total_amount FROM agg_trans GROUP BY state), district_transaction AS (
SELECT location AS district, SUM(transaction_count) AS total_transactions, 
SUM(transaction_amount) AS total_amount FROM top_trans GROUP BY location)
SELECT 'State' AS category, state AS name, total_transactions, total_amount
FROM state_transaction UNION ALL SELECT 'District', district, total_transactions, total_amount
FROM district_transaction ORDER BY total_amount DESC;



