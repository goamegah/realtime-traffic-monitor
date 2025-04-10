-- Prévue pour plus tard, quand on aura des prédictions ML
CREATE OR REPLACE VIEW traffic_predictions AS
SELECT
    f.datetime,
    f.location_id,
    f.avg_speed,
    p.predicted_status
FROM traffic_features_for_prediction f
         JOIN prediction_results p ON f.location_id = p.location_id AND f.datetime = p.datetime;
