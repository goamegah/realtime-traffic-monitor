CREATE TABLE IF NOT EXISTS traffic_stream (
    datetime TIMESTAMP,
    location_id TEXT,
    average_speed INTEGER,
    travel_time INTEGER,
    traffic_status TEXT,
    probe_count INTEGER,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    road_name TEXT,
    max_speed INTEGER,
    hierarchie TEXT,
    geometry_linestring JSONB
);
