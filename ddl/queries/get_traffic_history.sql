SELECT
    period,
    location_id,
    denomination,
    ROUND(vitesse_moyenne::numeric, 2) AS avg_speed,
    ROUND((1 - vitesse_moyenne / NULLIF(vitesse_maxi, 0))::numeric, 2) AS congestion,
    ROUND(temps_trajet_moyen::numeric, 2) AS travel_time
FROM traffic_stats_by_{{period}}  -- "minute" ou "hour"
WHERE period >= NOW() - INTERVAL '1 day'
  AND lat IS NOT NULL AND lon IS NOT NULL
ORDER BY period;
