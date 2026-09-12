@echo off
set ENV_NAME=finops-env

echo Setting up Conda environment for PyFlink (requires Python ^= 3.10)...

where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: conda was not found on PATH. See the README prerequisites.
    exit /b 1
)

call conda env list | findstr /i "\<%ENV_NAME%\>" >nul
if %errorlevel% equ 0 (
    echo Conda env '%ENV_NAME%' already exists; reusing it.
) else (
    call conda create -y -n %ENV_NAME% python=3.10
)

call conda activate %ENV_NAME%

echo Installing Python requirements...
call conda install -y -c conda-forge openjdk=11
call pip install setuptools==69.0.3
call pip install kafka-python==2.0.2
call pip install apache-flink==1.17.2 --no-build-isolation

echo Downloading Flink connectors into PyFlink's library folder...
for /f "delims=" %%i in ('python -c "import os, pyflink; print(os.path.join(os.path.dirname(pyflink.__file__), 'lib'))"') do set FLINK_LIB_DIR=%%i

if not exist "%FLINK_LIB_DIR%" mkdir "%FLINK_LIB_DIR%"
cd "%FLINK_LIB_DIR%"

if not exist "flink-sql-connector-kafka-1.17.2.jar" (
    curl -fsSL -O https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.17.2/flink-sql-connector-kafka-1.17.2.jar
)
if not exist "flink-connector-jdbc-3.1.1-1.17.jar" (
    curl -fsSL -O https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.1.1-1.17/flink-connector-jdbc-3.1.1-1.17.jar
)
if not exist "postgresql-42.6.0.jar" (
    curl -fsSL -O https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar
)

echo Setup complete! Run 'conda activate %ENV_NAME%' to enter the environment.
