#!/usr/bin/env python3

import argparse
import csv
import sys
import os

import os
import sys

def parse_kv_file(path):
    keys = []
    values = []

    base_dir = os.path.dirname(path)

    # 1) Skip if benchmark.log indicates a core dump
    log_path = os.path.join(base_dir, 'benchmark.log')
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', errors='replace') as log_file:
                for line in log_file:
                    if 'core dumped' in line:
                        print(f"Warning: 'core dumped' found in {log_path}", file=sys.stderr)
                        return [], []
        except Exception as e:
            print(f"Error reading {log_path}: {e}", file=sys.stderr)
            return [], []

    # 2) Skip if time.out indicates a command failure
    time_path = os.path.join(base_dir, 'time.out')
    if os.path.exists(time_path):
        try:
            with open(time_path, 'r', errors='replace') as time_file:
                for line in time_file:
                    if 'Command exited' in line:
                        print(f"Warning: 'Command exited' found in {time_path}", file=sys.stderr)
                        return [], []
        except Exception as e:
            print(f"Error reading {time_path}: {e}", file=sys.stderr)
            return [], []

    # 3) Proceed with parsing the key-value CSV
    try:
        with open(path, 'r', errors='replace') as f:
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
