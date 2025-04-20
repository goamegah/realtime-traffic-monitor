SELECT *
FROM {table}
WHERE road_name = %s
  AND period BETWEEN %s AND %s
ORDER BY period;
