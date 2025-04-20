CREATE OR REPLACE VIEW traffic_evolution_by_road_name AS
SELECT
    period,
    road_name,
    average_speed,
    average_travel_time,
    average_travel_time_reliability,
    max_speed,
    traffic_status_list
FROM road_traffic_stats_minute
ORDER BY period DESC;