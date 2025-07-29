#!/usr/bin/env python3

import argparse
import csv
import sys
import os

def parse_kv_file(path):
    keys = []
    values = []
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
        sys.exit(1)
    except Exception as e:
        print(f"Error while reading {path}: {e}", file=sys.stderr)
        sys.exit(1)
    return keys, values

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Input file with key,value pairs')
    args = parser.parse_args()

    keys, values = parse_kv_file(args.input_file)

    writer = csv.writer(sys.stdout)
    writer.writerow(keys)
    writer.writerow(values)
