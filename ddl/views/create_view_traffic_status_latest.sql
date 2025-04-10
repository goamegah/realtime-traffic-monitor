CREATE OR REPLACE VIEW traffic_status_latest AS
SELECT DISTINCT ON (location_id)
    datetime,
    location_id,
    average_speed,
    travel_time,
    traffic_status,
    lat,
    lon,
    road_name,
    max_speed,
    hierarchie
FROM traffic_stream
WHERE probe_count > 0
ORDER BY location_id, datetime DESC;
