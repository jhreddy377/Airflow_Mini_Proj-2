#!/usr/bin/env python3
"""
Airflow Log Analyzer
This script analyzes Airflow log files and reports errors found in them.
It recursively searches for all .log files in the specified directory,
parses error messages, and provides a cumulative report.
"""

from pathlib import Path
import re
import sys
from typing import Tuple, List


def analyze_file(file_path: str) -> Tuple[int, List[Tuple[str, str, str]]]:
    """
    Parse a log file and extract WARNING and ERROR entries.

    Args:
        file_path: Path to the log file to analyze

    Returns:
        tuple: (entry_count, log_entries_list)
            - entry_count: total number of WARNING/ERROR entries
            - log_entries_list: list of (timestamp, message_type, message) tuples
    """
    entry_count = 0
    log_entries = []

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Match lines containing WARNING or ERROR (case-insensitive)
                # Pattern: datetime, line number, message type, message
                match = re.search(
                    r'\{?.*?(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^}]*)\}?.*?(?P<level>warning|error)\b.*?(?P<message>.*?)$',
                    line,
                    re.IGNORECASE
                )
                
                if match:
                    entry_count += 1
                    timestamp = match.group('timestamp')
                    level = match.group('level').upper()
                    message = match.group('message').strip()
                    
                    # Try to extract cleaner message if JSON-like format
                    json_match = re.search(r'"event"\s*:\s*"([^"]*)"', line)
                    if json_match:
                        message = json_match.group(1)
                    elif not message or len(message) < 5:
                        message = line.strip()[:100]
                    
                    log_entries.append((timestamp, level, message))
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}", file=sys.stderr)

    return entry_count, log_entries


def analyze_logs(log_dir: str, symbol: str = None, log_level_filter: str = None) -> None:
    """
    Analyze all log files in a directory for WARNING and ERROR entries.

    Args:
        log_dir: Root directory containing log files
        symbol: Optional stock symbol filter (AAPL or TSLA)
        log_level_filter: Optional filter for log level (WARNING, ERROR, or comma-separated)
    """
    # Recursively find all .log files
    file_list = list(Path(log_dir).rglob('*.log'))

    if not file_list:
        print(f"No log files found in {log_dir}")
        return

    total_entries = 0
    all_log_entries = []
    files_analyzed = 0
    
    # Count by type
    type_counts = {'WARNING': 0, 'ERROR': 0}
    
    # Parse filter
    if log_level_filter:
        filter_types = [t.strip().upper() for t in log_level_filter.split(',')]
    else:
        filter_types = ['ERROR', 'WARNING']

    # Print header
    print(f"\n{'='*80}")
    if symbol:
        print(f"Log Analysis for {symbol}")
    else:
        print(f"Log Analysis for Directory: {log_dir}")
    if log_level_filter:
        print(f"Filter: {log_level_filter.upper()}")
    print(f"{'='*80}")

    # Analyze each log file
    for log_file in sorted(file_list):
        count, entries = analyze_file(str(log_file))
        if count > 0:
            files_analyzed += 1
            total_entries += count
            for timestamp, level, message in entries:
                all_log_entries.append((str(log_file), timestamp, level, message))
                type_counts[level] = type_counts.get(level, 0) + 1

    # Print statistics
    print(f"\nFiles Analyzed: {len(file_list)}")
    print(f"Files with Log Entries: {files_analyzed}")
    print(f"Total Log Entries Found: {total_entries}")
    print(f"\nBreakdown by Type:")
    print(f"  - WARNING: {type_counts['WARNING']}")
    print(f"  - ERROR:   {type_counts['ERROR']}")

    # Print log entries organized by type, filtered by requested type(s)
    if all_log_entries:
        for log_type in ['ERROR', 'WARNING']:
            if log_type not in filter_types:
                continue
                
            entries_of_type = [e for e in all_log_entries if e[2] == log_type]
            if entries_of_type:
                print(f"\n{log_type} Entries ({len(entries_of_type)}):")
                print("-" * 80)
                for i, (file_path, timestamp, level, message) in enumerate(entries_of_type, 1):
                    print(f"{i}. [{timestamp}] {level}")
                    print(f"   File: {file_path}")
                    print(f"   {message[:120]}")
                    print()
    else:
        print("\nNo log entries found.")

    print(f"{'='*70}\n")


def main():
    """Main entry point for the log analyzer."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python log_analyzer.py <log_directory> [symbol] [--level LEVEL]")
        print("\nArguments:")
        print("  log_directory: Path to the log directory to analyze")
        print("  symbol:        Optional stock symbol filter (AAPL, TSLA)")
        print("  --level:       Optional log level filter (ERROR, WARNING, or comma-separated)")
        print("\nExamples:")
        print("  python log_analyzer.py /opt/airflow/logs")
        print("  python log_analyzer.py /opt/airflow/logs AAPL")
        print("  python log_analyzer.py /opt/airflow/logs --level ERROR")
        print("  python log_analyzer.py /opt/airflow/logs --level ERROR,WARNING")
        sys.exit(1)

    log_dir = sys.argv[1]
    symbol = None
    log_level_filter = None
    
    # Parse remaining arguments
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == '--level' and i + 1 < len(sys.argv):
            log_level_filter = sys.argv[i + 1]
        elif not arg.startswith('--') and symbol is None:
            symbol = arg

    # Validate directory exists
    if not Path(log_dir).exists():
        print(f"Error: Directory '{log_dir}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Run analyzer
    analyze_logs(log_dir, symbol, log_level_filter)


if __name__ == '__main__':
    main()
