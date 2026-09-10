CREATE TABLE IF NOT EXISTS finops_cost (
    window_end TIMESTAMP,
    resource_id VARCHAR(255),
    total_cost_usd DOUBLE PRECISION,
    is_anomaly BOOLEAN
);
