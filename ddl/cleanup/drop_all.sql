-- Supprimer les vues si elles existent
DROP VIEW IF EXISTS traffic_status_latest CASCADE;
DROP VIEW IF EXISTS traffic_stats_per_minute_summary CASCADE;
DROP VIEW IF EXISTS traffic_stats_hourly_summary CASCADE;
DROP VIEW IF EXISTS traffic_sliding_window_summary CASCADE;

-- Supprimer la table principale
DROP TABLE IF EXISTS traffic_stream CASCADE;
DROP TABLE IF EXISTS traffic_stats_by_minute CASCADE;
DROP TABLE IF EXISTS traffic_stats_by_hour CASCADE;
DROP TABLE IF EXISTS traffic_stats_sliding_window CASCADE;

