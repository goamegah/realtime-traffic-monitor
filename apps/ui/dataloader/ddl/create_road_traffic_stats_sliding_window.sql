CREATE TABLE IF NOT EXISTS traffic_stats_sliding_window (
                                                            window_start TIMESTAMP,
                                                            window_end TIMESTAMP,
                                                            num_troncon INTEGER,
                                                            total_vehicle_probe INTEGER,
                                                            average_speed DOUBLE PRECISION,
                                                            average_travel_time DOUBLE PRECISION,
                                                            average_travel_time_reliability DOUBLE PRECISION,
                                                            road_name TEXT,
                                                            max_speed INTEGER,
                                                            traffic_status_list TEXT[]
);
