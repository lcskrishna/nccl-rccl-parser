import os
import sys
import argparse

coll_op_map = {
            "AllReduce": "all_reduce_perf",
            "Broadcast": "broadcast_perf",
          }

reduction_op_map = {
                "0" : "sum",
                "1" : "prod",
                "2" : "max",
                "3" : "min",
                "4" : "all",
               }

data_types_map = {
                "0" : "int8",
                "1" : "uint8",
                "2" : "int32",
                "3" : "uint32",
                "4" : "int64",
                "5" : "uint64",
                "6" : "half",
                "7" : "float",
                "8" : "double",
                "9" : "bf16",
                #"10" : "ncclNumTypes Equivalent?"
             }

data_type_bytes_map = {
                    "0" : 1,
                    "1" : 1,
                    "2" : 4,
                    "3" : 4,
                    "4" : 8,
                    "5" : 8,
                    "6" : 2,
                    "7" : 4,
                    "8" : 8,
                    "9" : 2,
                    #"10" : Not sure.
                  }
                
def get_useful_info(log_file):
    fs = open(log_file, 'r')
    lines = fs.readlines()
    fs.close()

    useful_lines = []
    for j in range(len(lines)):
        line = lines[j].rstrip()
        if ("opCount" in line and "sendbuff" in line):
            useful_lines.append(line)

    return useful_lines

def parse_nccl_log(nccl_lines):
    
    commands = []
    for j in range(len(nccl_lines)):
        line = nccl_lines[j]
        split_list = line.split(" ")
        comm = split_list[4].replace(":", "")
        count = split_list[12]
        datatype = split_list[14]
        op_type = split_list[16]
        root = split_list[18]
        nnranks = split_list[21].split("=")[1].replace("]", "")

        #print (comm)
        #print (count)
        #print (datatype)
        #print (op_type)
        #print (root)
        #print (nnranks)

        total_bytes = int(count) * data_type_bytes_map[datatype]

        test_cmd = "./build/" + coll_op_map[comm] + " -d " + data_types_map[datatype] + \
                       " -b " + str(total_bytes) + " -e " + str(total_bytes) + \
                       " -o " + reduction_op_map[op_type] + " -g " + str(nnranks)
        #print (test_cmd)
        commands.append(test_cmd)

    return commands

def generate_script(commands, output_script):
    fs = open(output_script + ".sh", "w")
    for j in range(len(commands)):
        fs.write(commands[j])
        fs.write("\n")
    fs.close()
    print("INFO: Dumped out the commands in a script named: {}".format(output_script))

def dump_counts_map(counts_map, output_file):
    fs = open(output_file + ".csv", 'w')
    fs.write("sep=|")
    fs.write("\n")
    keys = counts_map.keys()
    for key in keys:
        fs.write(key + "|" + str(counts_map[key]))
        fs.write("\n")
    fs.close()
    print ("INFO: Done dumping the count map of each command.")

def get_unique_commands(commands):
    unique_values = []
    counts_map = {}
    for j in range(len(commands)):
        cmd = commands[j]
        if (cmd not in unique_values):
            counts_map[cmd] = 1
            unique_values.append(cmd)
        else:
            counts_map[cmd] = counts_map[cmd] + 1
    return unique_values, counts_map

def main():
    log_file = os.path.abspath(args.nccl_debug_log)
    nccl_lines = get_useful_info(log_file)
    commands = parse_nccl_log(nccl_lines)
    #generate_script(commands, args.output_script_name)
    if (args.unique):
        new_commands, counts_map = get_unique_commands(commands)
        generate_script(new_commands, args.output_script_name + "_unique")
        dump_counts_map(counts_map, args.output_script_name + "_counts")
    else:
        generate_script(commands, args.output_script_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--nccl-debug-log", type=str, required=True, help="Log from app with NCCL_DEBUG=INFO NCCL_DEBUG_SUBSYS=INIT,COLL")
    parser.add_argument("--output-script-name", type=str, required=False, default="net_nccl_rccl", help="Output command script")
    parser.add_argument("--unique", action="store_true", default=False, help="Get only the unique commands.")

    args = parser.parse_args()
    main()
