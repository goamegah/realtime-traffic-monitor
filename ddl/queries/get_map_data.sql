SELECT
    location_id,
    road_name AS route_id,
    lat,
    lon,
    ROUND(average_speed::numeric, 2) AS avg_speed,
    ROUND((1 - average_speed / NULLIF(max_speed, 0))::numeric, 2) AS congestion_level
FROM traffic_status_latest
WHERE lat IS NOT NULL AND lon IS NOT NULL;
