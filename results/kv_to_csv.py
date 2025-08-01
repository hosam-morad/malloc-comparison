#!/usr/bin/env python3

import argparse
import csv
import sys
import os

def parse_kv_file(path):
    keys = []
    values = []

    # Check for core dump indication in benchmark.log
    log_path = os.path.join(os.path.dirname(path), 'benchmark.log')
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r') as log_file:
                if 'core dumped' in log_file.read():
                    print(f"Warning: 'core dumped' found in {log_path}", file=sys.stderr)
                    return [], []
        except Exception as e:
            print(f"Error reading {log_path}: {e}", file=sys.stderr)
            return [], []

    # Proceed with parsing the key-value CSV
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                key, value = line.split(',', 1)
                keys.append(key.strip())
                values.append(value.strip())
    except FileNotFoundError:
        print(f"Error: file not found: {path}", file=sys.stderr)
        return [], []
    except Exception as e:
        print(f"Error while reading {path}: {e}", file=sys.stderr)
        return [], []

    return keys, values

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Input file with key,value pairs')
    args = parser.parse_args()

    keys, values = parse_kv_file(args.input_file)

    writer = csv.writer(sys.stdout)
    writer.writerow(keys)
    writer.writerow(values)
