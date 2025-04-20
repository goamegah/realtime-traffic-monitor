SELECT MIN(period) AS min_period, MAX(period) AS max_period
FROM {table}
WHERE road_name = %s;
