SELECT
    COUNT(DISTINCT location_id) AS nb_points_actifs,
    ROUND(AVG(average_speed)::numeric, 2) AS vitesse_moyenne,
    ROUND(AVG(1 - average_speed / NULLIF(max_speed, 0))::numeric, 2) AS congestion_moyenne
FROM traffic_status_latest
WHERE average_speed IS NOT NULL AND max_speed > 0;
