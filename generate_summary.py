import os
import sys
import argparse

def get_script_commands(script_file):
    fs = open(script_file, 'r')
    lines = fs.readlines()
    fs.close()

    commands = []
    for j in range(len(lines)):
        line = lines[j].rstrip()
        commands.append(line)

    return commands

def parse_useful_information(log_file):
    fs = open(log_file, 'r')
    lines = fs.readlines()
    fs.close()

    useful_lines = []
    for j in range(len(lines)):
        line = lines[j].rstrip()
        if ("time" in line and "algbw" in line and "busbw" in line):
            perf_line = lines[j+2]
            if ("Avg bus bandwidth" in lines[j+5]):
                perf_line = perf_line + lines[j + 5]
            elif ("Avg bus bandwidth" in lines[j+4]):
                perf_line = perf_line + lines[j+4]
            useful_lines.append(perf_line)
    return useful_lines

def parse_nccl_performance(useful_lines, commands):
    
    perf_lines = []
    perf_lines.append("sep=|")
    perf_lines.append("size|count|type|redop|time-oplace(us)|algbw(gb/s)-oplace|busbw(gb/s)-oplace|error|" + \
                        "time-iplace(us)|algbw(gb/s)-iplace|busbw(gb/s)-iplace|error|avg_bus_bw")
    for j in range(len(useful_lines)):
        line = useful_lines[j]
        line = line.replace("# Avg bus bandwidth    : ", "")
        
        split_list = line.split()
        perf_line = ""
        for i in range(len(split_list)):
            perf_line = perf_line + split_list[i] + "|"
        #print (perf_line + commands[j])
        perf_lines.append(perf_line + commands[j])

    return perf_lines
        
def generate_output_file(out_file, perf_lines):
    fs = open(out_file, 'w')
    for j in range(len(perf_lines)):
        fs.write(perf_lines[j])
        fs.write('\n')
    fs.close()
    print ("INFO: Dumped out the performance.")

def main():
    log_file = os.path.abspath(args.log_file)
    out_file = args.output_file_name + ".csv"
    script_file = os.path.abspath(args.script_file)

    commands = get_script_commands(script_file)
    useful_lines = parse_useful_information(log_file)
    perf_lines = parse_nccl_performance(useful_lines, commands)
    generate_output_file(out_file, perf_lines)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-file", type=str, required=True, help="Log file generated while running rccl-tests")
    parser.add_argument("--output-file-name", type=str, required=False, default="net_summary")
    parser.add_argument("--script-file", type=str, required=True, help="Script file to run NCCL/RCCL Tests")

    args = parser.parse_args()
    main()
