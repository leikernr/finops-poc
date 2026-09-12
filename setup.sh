#!/bin/bash
set -e

ENV_NAME="finops-env"

echo "Setting up Conda environment for PyFlink (requires Python <= 3.10)..."

# Fail immediately if conda is missing. Without this guard the command
# substitution below expands to an empty string, `eval ""` succeeds, and the
# first error the user sees comes from `conda create` on the next line --
# which reads as an env-creation problem rather than "conda is not installed".
if ! command -v conda >/dev/null 2>&1; then
    echo "ERROR: conda was not found on PATH. See the README prerequisites." >&2
    exit 1
fi

eval "$(conda shell.bash hook)"

# Creating an env that already exists is an error, and under `set -e` that
# aborts the script -- so re-running setup.sh after any earlier failure failed
# again, at a different line. The JAR downloads below are already guarded for
# re-runs; this makes env creation behave the same way.
if conda env list | awk '{print $1}' | grep -qx "$ENV_NAME"; then
    echo "Conda env '$ENV_NAME' already exists; reusing it."
else
    conda create -y -n "$ENV_NAME" python=3.10
fi

conda activate "$ENV_NAME"

CONDA_PIP="$CONDA_PREFIX/bin/pip"

echo "Installing Python requirements..."
$CONDA_PIP install setuptools==69.0.3
$CONDA_PIP install kafka-python==2.0.2
$CONDA_PIP install apache-flink==1.17.2 --no-build-isolation

# Flink 1.17 targets Java 11. Install it into the env rather than depending on
# whatever JDK happens to be on the host PATH, which is the single most
# variable prerequisite here -- Homebrew, apt and the Adoptium installer all
# hand out a current JDK by default. Installing it here keeps the system Java
# untouched and puts the right one first on PATH only while the env is active.
# A JDK mismatch does not fail in this script; it fails much later, inside
# anomaly_detector.py, as a JVM error surfaced through a Python stack trace.
if "$CONDA_PREFIX/bin/java" -version >/dev/null 2>&1; then
    echo "Java already present in the env: $("$CONDA_PREFIX/bin/java" -version 2>&1 | head -1)"
else
    echo "Installing Java 11 into the environment (Flink 1.17 targets Java 11)..."
    conda install -y -c conda-forge openjdk=11
fi

# Pick whichever downloader this machine actually has, rather than assuming one.
# macOS ships curl and no wget; most Linux distros ship both; minimal images
# (Fedora minimal, RHEL UBI) often ship only curl.
if command -v curl >/dev/null 2>&1; then
    download() { curl -fsSL -O "$1"; }
elif command -v wget >/dev/null 2>&1; then
    download() { wget -q "$1"; }
else
    echo "ERROR: neither curl nor wget is installed; cannot fetch the Flink connectors." >&2
    exit 1
fi

echo "Downloading Flink connectors straight into PyFlink's library folder to bypass Java 17 errors..."
FLINK_LIB_DIR="$CONDA_PREFIX/lib/python3.10/site-packages/pyflink/lib"
mkdir -p "$FLINK_LIB_DIR"

cd "$FLINK_LIB_DIR"

if [ ! -f "flink-sql-connector-kafka-1.17.2.jar" ]; then
    download https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
fi
if [ ! -f "flink-connector-jdbc-3.1.1-1.17.jar" ]; then
    download https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.1.1-1.17/flink-connector-jdbc-3.1.1-1.17.jar
fi
if [ ! -f "postgresql-42.6.0.jar" ]; then
    download https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar
fi

echo "Setup complete! Run 'conda activate finops-env' to enter the environment."
