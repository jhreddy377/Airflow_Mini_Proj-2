# Log Analyzer - Airflow Mini Project - 2

Python utility for analyzing Airflow log files to identify and report ERROR's and WARNING's.

## Overview

The Log Analyzer scans log files recursively within a specified directory, extracts ERROR and WARNING messages with their timestamps, and generates a comprehensive report. 

## Features

- **Recursive log scanning**: Recursively finds all `.log` files in the specified DAGS Log directory
- **Error/Warning extraction**: Identifies and extracts ERROR and WARNING level messages
- **JSON format handling**: It can parse JSON-formatted log entries
- **filtering**: Filter logs by stock symbol or log level
- **Detailed reporting**: Organized output with file paths, timestamps, and message content
- **Error handling**: Gracefully handles file encoding and read errors

## Installation

Ensure you have Python 3.x installed. No additional python libraries are required

## Usage

### Basic Syntax

```bash
python log_analyzer.py <log_directory> [symbol] [--level LEVEL]
```

### Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `log_directory` | Required | Path to the root directory containing log files to analyze |
| `symbol` | Optional | Filter results by stock symbol (e.g., AAPL, TSLA) |
| `--level` | Optional | Filter by log level: `ERROR`, `WARNING`, or comma-separated list |

### Examples

#### Analyze all logs in a directory
```bash
python log_analyzer.py /opt/airflow/logs
```

#### Filter Errors/Warnings by stock symbol
```bash
python log_analyzer.py /opt/airflow/logs AAPL
```

#### Filter Errors Only
```bash
python log_analyzer.py /opt/airflow/logs --level ERROR
```

#### Filter by multiple log levels
```bash
python log_analyzer.py /opt/airflow/logs --level ERROR,WARNING
```



## Output

The script generates a formatted report containing:

- **File Statistics**: Total files analyzed, files with log entries, total entries found
- **Breakdown by Type**: Count of ERROR and WARNING entries
- **Detailed Entries**: Organized by log level with:
  - Timestamp
  - Log level type (ERROR/WARNING)
  - File path
  - Error/warning message (first 120 characters)

Example output:
```
================================================================================
Log Analysis for Directory: /opt/airflow/logs
================================================================================

Files Analyzed: 45
Files with Log Entries: 12
Total Log Entries Found: 28

Breakdown by Type:
  - WARNING: 15
  - ERROR:   13

ERROR Entries (13):
--------------------------------------------------------------------------------
1. [2026-03-10T17:49:01.761755+0000] ERROR
   File: /opt/airflow/logs/dag_id=marketvol/run_id=manual__2026-03-10T174901.761755+0000/task_id=t0/attempt=1.log
   Connection failed: timeout on task execution
...
```

## Docker Usage

Run the analyzer inside an Airflow Docker container:

```bash
docker compose exec -T airflow-scheduler python /opt/airflow/logs log_analyzer.py <log_directory>
```

Example:
```bash
docker compose exec -T airflow-scheduler python /opt/airflow/dags/log_analyzer.py /opt/airflow/logs/dag_id=marketvol
```
