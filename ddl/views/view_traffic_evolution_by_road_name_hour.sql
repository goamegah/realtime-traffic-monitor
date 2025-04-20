CREATE OR REPLACE VIEW traffic_evolution_by_road_name_hour AS
SELECT
    period,
    road_name,
    average_speed,
    average_travel_time,
    total_vehicle_probe,
    num_troncon,
    traffic_status_list
FROM road_traffic_stats_hour
WHERE road_name IS NOT NULL
ORDER BY period;
