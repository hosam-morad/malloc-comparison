#! /usr/bin/env python3

import sys
import os
import argparse
import subprocess


def parse_arguments():
    parser = argparse.ArgumentParser(description='A tool to run applications while\
             pre-loading mosalloc library to intercept allocation calls and\
             redirect them to pre-allocated regions backed with mixed pages sizes')
    parser.add_argument('-l', '--library', default='src/morecore/lib_morecore.so',
                        help="mosalloc library path to preload.")
    parser.add_argument('dispatch_program', help="program to execute")
    parser.add_argument('dispatch_args', nargs=argparse.REMAINDER,
                        help="program arguments")
    args = parser.parse_args()

    # validate the command-line arguments
    if not os.path.isfile(args.library):
        sys.exit(f"Error: the malloc library {args.library} cannot be found")

    return args


def run_benchmark(environ):
    try:
        command_line = [args.dispatch_program] + args.dispatch_args
        print(f"Running: {' '.join(command_line)} with LD_PRELOAD={environ['LD_PRELOAD']}")
        p = subprocess.Popen(command_line, env=environ, shell=False)
        p.wait()
    except Exception as e:
        raise e
    
    sys.exit(p.returncode)

args = parse_arguments()

environ = os.environ

# update the LD_PRELOAD to include our library besides others if exist
ld_preload = os.environ.get("LD_PRELOAD")
if ld_preload is None:
    environ["LD_PRELOAD"] = args.library
else:
    environ["LD_PRELOAD"] = ld_preload + ':' + args.library

# dispatch the program with the environment we just set
run_benchmark(environ)