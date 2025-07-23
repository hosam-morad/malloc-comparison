#! /bin/bash

if (( $# < 1 )); then
    echo "Usage: $0 \"command_to_execute\""
    exit -1
fi

command="$@"

time_format="seconds-elapsed,%e\nuser-time-seconds,%U\n"
time_format+="kernel-time-seconds,%S\nmax-resident-memory-kb,%M\n"
time_format+="major-page-faults,%F\nminor-page-faults,%R\ncontext-switches,%c"
time_command="/usr/bin/time --format=$time_format --output=time.out"

submit_command="$time_command"
echo "Running the following command:"
echo "$submit_command $command"
$submit_command $command
