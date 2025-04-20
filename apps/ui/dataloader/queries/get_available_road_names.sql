SELECT DISTINCT road_name
FROM {table}
WHERE road_name IS NOT NULL
ORDER BY road_name;
