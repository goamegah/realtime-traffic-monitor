CREATE OR REPLACE VIEW traffic_stats_per_minute AS
SELECT
    date_trunc('minute', datetime) AS minute,
    COUNT(*) AS segment_count,
    AVG(average_speed) AS avg_speed,
    SUM(CASE WHEN traffic_status = 'congested' THEN 1 ELSE 0 END) AS congestion_count
FROM traffic_stream
GROUP BY 1
ORDER BY 1 DESC;
