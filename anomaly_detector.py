import logging
import os

from pyflink.table import EnvironmentSettings, TableEnvironment

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    db_password = os.getenv("POSTGRES_PASSWORD", "finops_password")
    db_user = os.getenv("POSTGRES_USER", "finops")
    anomaly_threshold = os.getenv("ANOMALY_THRESHOLD", "10.0")

    logger.info("Initializing Flink Table Environment...")
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    t_env.get_config().set("pipeline.closure-cleaner-level", "NONE")
    t_env.get_config().set("table.exec.source.idle-timeout", "1000 ms")

    logger.info("Defining Kafka Source Table...")
    t_env.execute_sql("""
        CREATE TABLE cloud_metrics (
            `timestamp` TIMESTAMP(3),
            resource_id STRING,
            cpu_usage DOUBLE,
            WATERMARK FOR `timestamp` AS `timestamp` - INTERVAL '2' SECONDS
        ) WITH (
            'connector' = 'kafka',
            'topic' = 'cloud_metrics',
            'properties.bootstrap.servers' = 'localhost:9092',
            'properties.group.id' = 'finops_group',
            'format' = 'json',
            'scan.startup.mode' = 'latest-offset'
        )
    """)

    logger.info("Defining Postgres Sink Table...")
    t_env.execute_sql(f"""
        CREATE TABLE finops_cost (
            window_end TIMESTAMP(3),
            resource_id STRING,
            total_cost_usd DOUBLE,
            is_anomaly BOOLEAN
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://localhost:5432/finops_db',
            'table-name' = 'finops_cost',
            'username' = '{db_user}',
            'password' = '{db_password}'
        )
    """)

    logger.info("Starting Streaming Job...")
    t_env.execute_sql(f"""
        INSERT INTO finops_cost
        SELECT 
            TUMBLE_END(`timestamp`, INTERVAL '10' SECONDS) AS window_end,
            resource_id,
            SUM(cpu_usage * 0.05) AS total_cost_usd,
            SUM(cpu_usage * 0.05) > {anomaly_threshold} AS is_anomaly
        FROM cloud_metrics
        GROUP BY TUMBLE(`timestamp`, INTERVAL '10' SECONDS), resource_id
    """).wait()

if __name__ == '__main__':
    main()
