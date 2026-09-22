# CREATE DATABASE acoustic_anomaly_db;
USE acoustic_anomaly_db;
SELECT DATABASE();

DESCRIBE recordings;
SELECT COUNT(*) AS total_recordings
FROM recordings;
SELECT *
FROM recordings
LIMIT 10;




USE acoustic_anomaly_db;

DESCRIBE acoustic_features;

USE acoustic_anomaly_db;

SELECT COUNT(*) AS total_features
FROM acoustic_features;

USE acoustic_anomaly_db;

DESCRIBE anomaly_results;

SELECT *
FROM anomaly_results
LIMIT 5;

SELECT COUNT(*) AS total_results
FROM anomaly_results;

USE acoustic_anomaly_db;

SELECT
    r.recording_id,
    r.sensor_id,
    r.recording_date,
    r.hour,
    a.ensemble_pct,
    a.models_above_90,
    a.deviation_level
FROM recordings AS r
INNER JOIN anomaly_results AS a
    ON r.recording_id = a.recording_id;
    
    SELECT
    r.recording_id,
    r.sensor_id,
    r.recording_date,
    r.hour,

    a.ensemble_pct,
    a.models_above_90,
    a.deviation_level,

    f.rms_mean,
    f.rms_std,
    f.zcr_mean,
    f.zcr_std

FROM recordings AS r

INNER JOIN anomaly_results AS a
    ON r.recording_id = a.recording_id

INNER JOIN acoustic_features AS f
    ON r.recording_id = f.recording_id;
    
#SELECT COUNT(*) AS recordings_without_results
#FROM recordings r
#LEFT JOIN anomaly_results a
 #   ON r.recording_id = a.recording_id
#WHERE a.recording_id IS NULL

SELECT COUNT(*) AS recordings_without_features
FROM recordings r
LEFT JOIN acoustic_features f
    ON r.recording_id = f.recording_id
WHERE f.recording_id IS NULL;

SELECT
    deviation_level,
    COUNT(*) AS total_recordings
FROM anomaly_results
GROUP BY deviation_level
ORDER BY total_recordings DESC;

