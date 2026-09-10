#!/bin/bash
set -e

echo "Setting up Conda environment for PyFlink (requires Python <= 3.10)..."
eval "$(conda shell.bash hook)"
conda create -y -n finops-env python=3.10
conda activate finops-env

CONDA_PIP="$CONDA_PREFIX/bin/pip"

echo "Installing Python requirements..."
$CONDA_PIP install setuptools==69.0.3
$CONDA_PIP install kafka-python==2.0.2
$CONDA_PIP install apache-flink==1.17.2 --no-build-isolation

echo "Downloading Flink connectors straight into PyFlink's library folder to bypass Java 17 errors..."
FLINK_LIB_DIR="$CONDA_PREFIX/lib/python3.10/site-packages/pyflink/lib"
mkdir -p "$FLINK_LIB_DIR"

cd "$FLINK_LIB_DIR"

if [ ! -f "flink-sql-connector-kafka-1.17.2.jar" ]; then
    wget https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
fi
if [ ! -f "flink-connector-jdbc-3.1.1-1.17.jar" ]; then
    wget https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.1.1-1.17/flink-connector-jdbc-3.1.1-1.17.jar
fi
if [ ! -f "postgresql-42.6.0.jar" ]; then
    wget https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar
fi

echo "Setup complete! Run 'conda activate finops-env' to enter the environment."
