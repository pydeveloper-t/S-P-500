-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ohlcv_1d
CREATE TABLE IF NOT EXISTS ohlcv_1d (
    ticker TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);


-- ohlcv_1h
CREATE TABLE IF NOT EXISTS ohlcv_1h (
    ticker TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);


-- ohlcv_5m
CREATE TABLE IF NOT EXISTS ohlcv_5m (
    ticker TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume BIGINT NOT NULL,
    PRIMARY KEY (symbol, timestamp)
);

SELECT create_hypertable('ohlcv_1d', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '30 days');
SELECT create_hypertable('ohlcv_1h', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '7 days');
SELECT create_hypertable('ohlcv_5m', 'timestamp', if_not_exists => TRUE, chunk_time_interval => INTERVAL '1 day');

