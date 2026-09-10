import os
from pyflink.table import EnvironmentSettings, TableEnvironment

def main():
    print("Initializing Flink Table Environment...")
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    t_env.get_config().set("pipeline.closure-cleaner-level", "NONE")
    t_env.get_config().set("table.exec.source.idle-timeout", "1000 ms")

    print("Defining Kafka Source Table...")
    t_env.execute_sql("""
        CREATE TABLE cloud_metrics (
            `timestamp` TIMESTAMP(3),
            `resource_id` STRING,
            `cpu_usage` DOUBLE,
            WATERMARK FOR `timestamp` AS `timestamp` - INTERVAL '2' SECOND
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'cloud_metrics',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'finops_group',
            'format' = 'json',
            'scan.startup.mode' = 'latest-offset'
        )
    """)

    print("Defining Postgres Sink Table...")
    t_env.execute_sql("""
        CREATE TABLE finops_cost (
            `window_end` TIMESTAMP(3),
            `resource_id` STRING,
            `total_cost_usd` DOUBLE,
            `is_anomaly` BOOLEAN
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://localhost:5432/finops_db',
            'table-name' = 'finops_cost',
            'username' = 'finops',
            'password' = 'finops_password'
        )
    """)

    print("Starting Streaming Job...")
    t_env.execute_sql("""
        INSERT INTO finops_cost
        SELECT 
            TUMBLE_END(`timestamp`, INTERVAL '10' SECONDS) as `window_end`,
            `resource_id`,
            SUM(cpu_usage * 0.05) AS total_cost_usd,
            SUM(cpu_usage * 0.05) > 10.0 AS is_anomaly
        FROM cloud_metrics
        GROUP BY TUMBLE(`timestamp`, INTERVAL '10' SECONDS), `resource_id`
    """).wait()

if __name__ == '__main__':
    main()
