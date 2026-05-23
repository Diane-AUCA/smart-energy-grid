Smart Energy Grid - SQL Scripts

Step 1: Create energy_readings table
====================================

CREATE TABLE energy_readings (
    meter_id TEXT,
    timestamp TIMESTAMPTZ NOT NULL,
    power DOUBLE PRECISION,
    voltage DOUBLE PRECISION,
    current DOUBLE PRECISION,
    frequency DOUBLE PRECISION,
    energy DOUBLE PRECISION
);

Step 2: Convert to hypertable
=============================

SELECT create_hypertable('energy_readings', 'timestamp', chunk_time_interval => INTERVAL '1 day');

Step 3: Create additional hypertables
=====================================

CREATE TABLE energy_readings_3h (LIKE energy_readings INCLUDING ALL);
CREATE TABLE energy_readings_week (LIKE energy_readings INCLUDING ALL);

SELECT create_hypertable('energy_readings_3h', 'timestamp', chunk_time_interval => INTERVAL '3 hours');
SELECT create_hypertable('energy_readings_week', 'timestamp', chunk_time_interval => INTERVAL '1 week');

Step 4: Baseline queries
========================

Query 1: Average power per hour today
-------------------------------------

SELECT time_bucket('1 hour', timestamp) AS hour, AVG(power) as avg_power
FROM energy_readings WHERE timestamp >= DATE_TRUNC('day', NOW())
GROUP BY hour ORDER BY hour;

Query 2: Peak consumption past week
-----------------------------------

SELECT time_bucket('15 minutes', timestamp) AS period, AVG(power) as avg_power
FROM energy_readings
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY period ORDER BY avg_power DESC LIMIT 10;

Query 3: Monthly consumption per meter
--------------------------------------

SELECT meter_id, DATE_TRUNC('month', timestamp) as month, SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, month
ORDER BY month, total_energy DESC;

Query 4: Full dataset scan
--------------------------

SELECT COUNT(*), AVG(power), MAX(power), MIN(power) FROM energy_readings;

Step 5: Compression
===================

ALTER TABLE energy_readings SET (timescaledb.compress, timescaledb.compress_orderby = 'timestamp DESC');
SELECT add_compression_policy('energy_readings', INTERVAL '24 hours');

ALTER TABLE energy_readings_3h SET (timescaledb.compress, timescaledb.compress_orderby = 'timestamp DESC');
SELECT add_compression_policy('energy_readings_3h', INTERVAL '24 hours');

ALTER TABLE energy_readings_week SET (timescaledb.compress, timescaledb.compress_orderby = 'timestamp DESC');
SELECT add_compression_policy('energy_readings_week', INTERVAL '24 hours');

Step 6: Continuous aggregations
===============================

CREATE MATERIALIZED VIEW energy_readings_15min
WITH (timescaledb.continuous) AS
SELECT meter_id,
    time_bucket('15 minutes', timestamp) AS bucket,
    AVG(power) as avg_power,
    MAX(power) as max_power,
    SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

CREATE MATERIALIZED VIEW energy_readings_1h
WITH (timescaledb.continuous) AS
SELECT meter_id,
    time_bucket('1 hour', timestamp) AS bucket,
    AVG(power) as avg_power,
    MAX(power) as max_power,
    SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

CREATE MATERIALIZED VIEW energy_readings_1day
WITH (timescaledb.continuous) AS
SELECT meter_id,
    time_bucket('1 day', timestamp) AS bucket,
    AVG(power) as avg_power,
    MAX(power) as max_power,
    SUM(energy) as total_energy
FROM energy_readings
GROUP BY meter_id, bucket;

Refresh policies
================

SELECT add_continuous_aggregate_policy('energy_readings_15min',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes');

SELECT add_continuous_aggregate_policy('energy_readings_1h',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

SELECT add_continuous_aggregate_policy('energy_readings_1day',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 day');

Performance tracking tables
===========================

CREATE TABLE query_performance (
    query_name TEXT,
    approach TEXT,
    execution_time_ms FLOAT
);

CREATE TABLE compression_stats (
    table_name TEXT,
    size_before_mb FLOAT,
    size_after_mb FLOAT
);

CREATE TABLE chunk_performance (
    query_name TEXT,
    chunk_3h_ms FLOAT,
    chunk_1day_ms FLOAT,
    chunk_1week_ms FLOAT
);
