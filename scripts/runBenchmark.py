#! /usr/bin/env python3

import sys
import os
import time
import subprocess
import shutil
import shlex
import csv
from os.path import join, getsize, islink

class BenchmarkRun:
    def __init__(self, benchmark_dir, output_dir):
        self._benchmark_dir = benchmark_dir
        if not os.path.exists(self._benchmark_dir):
            sys.exit('Error: the benchmark path ' + self._benchmark_dir + ' was not found.')

        self._output_dir = os.getcwd() + '/' + output_dir
        print('creating a new output directory', self._output_dir, '...')
        print('copying the benchmark files to ' + self._output_dir + '...')
        # symlinks are copied as symlinks with symlinks=True
        shutil.copytree(self._benchmark_dir, self._output_dir, symlinks=True)

        log_file_name = self._output_dir + '/benchmark.log'
        self._log_file = open(log_file_name, 'w')
        self.iterations = self.get_num_iterations() 
        self.repeated = True if self.iterations > 1 else False
        self._time_out_file=None
        self.minRunTime = 30 
    def __del__(self):
        if hasattr(self, "_log_file"):
            self._log_file.close()

    def get_num_iterations(self):
        # this fucntion checks if there any repetitions of all the 
        norm = os.path.normpath(self._output_dir)           
        pathsplitted = [p for p in norm.split(os.sep) if p]  
        pathsplittedUnrepeated=pathsplitted[:-1]
        mallocs = ['mimalloc','dlmalloc','ptmalloc2']
        indexOfMalloc=4
        it = 1
        for malloc in mallocs:
            tempL=pathsplittedUnrepeated.copy()
            tempL[4]=malloc 
            time_out_path_abs = os.path.join(os.sep, *tempL, "repeat1", "time.out")        
            if os.path.exists(time_out_path_abs) == True:
                with open (time_out_path_abs,"r") as f:
                    kv = {k.strip(): v.strip() for k, v in csv.reader(f) if k}
                    iterations = kv.get("iterations")
                    if iterations is not None:
                        it = int(float(iterations))
                        break 
        print(f"the number of init iterations is {it}")
        return it
    def prerun(self):
        print('warming up before running...')
        os.chdir(self._output_dir)
        # the prerun script will read input files to force them to reside
        # in the page-cache before run() is invoked.
        subprocess.check_call('./prerun.sh', stdout=self._log_file, stderr=self._log_file)

    def run(self, num_threads, submit_command):
        print('running the benchmark ' + self._benchmark_dir + '...')
        print('the full submit command is:\n\t' + submit_command + ' ./run.sh')
        environment_variables = {"OMP_NUM_THREADS": str(num_threads),
                "OMP_THREAD_LIMIT": str(num_threads)}
        environment_variables.update(os.environ)
        os.chdir(self._output_dir)
        self._run_process = subprocess.Popen(shlex.split(submit_command + ' ./run.sh'),
                stdout=self._log_file, stderr=self._log_file, env=environment_variables)

    def wait(self,num_threads, submit_command):
        print('waiting for the run to complete...')
        time_out_path = self._output_dir + '/time.out'
        it = self.iterations
        while True:
            self._run_process.wait()
            with open(time_out_path, 'r') as f:
                current_time_out = {k.strip(): float(v) for k, v in csv.reader(f)}
                currentSeconds=current_time_out['seconds-elapsed']
                if  self._time_out_file==None:
                    #print("temp has been saved")
                    self._time_out_file=current_time_out
                else :
                    for key in current_time_out.keys():
                        self._time_out_file[key]+=current_time_out[key]

                #the section above is for agregating the result of the runs 
            if self._time_out_file['seconds-elapsed']  < self.minRunTime and self.repeated == False:
                # current run time isn't enough we have to perform a loop
                self.iterations = self. minRunTime // currentSeconds + 1
                it = self.iterations
                #print(f"new iterations number is : f{it}")
                self.repeated=True
                self._time_out_file=None
                self.run(num_threads,submit_command)
                continue
            #print(" passed the first run and a new run time has been calculated ")
            it -= 1
            #print (f'it ={it} and self itertations={self.iterations}')
            if it > 0:
                self.run(num_threads,submit_command)
                continue
            elif self._run_process.returncode != 0:
                raise subprocess.CalledProcessError(self._run_process.returncode, ' '.join(self._run_process.args))
            else:
                break
        with open(time_out_path, "w") as f:
            self._time_out_file['iterations']=self.iterations
            writer = csv.writer(f)
            writer.writerows(self._time_out_file.items())
        print('sleeping a bit to let the filesystem recover...')
        time.sleep(3) # seconds

    def postrun(self):
        print('validating the run outputs...')
        os.chdir(self._output_dir)
        subprocess.check_call('./postrun.sh', stdout=self._log_file, stderr=self._log_file)

    def clean(self, exclude_files=[], threshold=1024*1024):
        print('cleaning large files from the output directory...')
        for root, dirs, files in os.walk('./'):
            for name in files:
                file_path = join(root, name)
                # remove files larger than threshold (default is 1MB)
                if (not islink(file_path)) and (getsize(file_path) > threshold) and (name not in exclude_files):
                    os.remove(file_path)
        print('syncing to clean all pending I/O activity...')
        os.sync()

import argparse
def getCommandLineArguments():
    parser = argparse.ArgumentParser(description='This python script runs a single benchmark, \
            possibly with a prefixing submit command like \"perf stat --\". \
            The script creates a new output directory in the current working directory, \
            copy the benchmark files there, and then prerun, run, and postrun the benchmark. \
            Finally, the script deletes large files (> 1MB) residing in the output directory.')
    parser.add_argument('-n', '--num_threads', type=int, default=4,
            help='the number of threads (for multi-threaded benchmark)')
    parser.add_argument('-s', '--submit_command', type=str, default='',
            help='a command that will prefix running the benchmark, e.g., "perf stat --".')
    parser.add_argument('-x', '--exclude_files', type=str, nargs='*', default=[],
            help='list of files to not remove')
    parser.add_argument('-f', '--force', action='store_true', default=False,
            help='run the benchmark anyway even if the output directory already exists')
    parser.add_argument('benchmark_dir', type=str, help='the benchmark directory, must contain three \
            bash scripts: prerun.sh, run.sh, and postrun.sh')
    parser.add_argument('output_dir', type=str, help='the output directory which will be created for \
            running the benchmark on a clean slate')
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = getCommandLineArguments()

    if os.path.exists(args.output_dir):
        print('Skipping the run because output directory', args.output_dir, 'already exists.')
        print('You can use the \'-f\' flag to suppress this message and run the benchmark anyway.')
    else:
        benchmark_run = BenchmarkRun(args.benchmark_dir, args.output_dir)
        benchmark_run.prerun()
        benchmark_run.run(args.num_threads, args.submit_command)
        benchmark_run.wait(args.num_threads, args.submit_command)
        benchmark_run.postrun()
        benchmark_run.clean(args.exclude_files)