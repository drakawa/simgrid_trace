import csv
import argparse
import glob
import math
import subprocess
from collections import defaultdict as dd
import re

from purify_trace import *

if __name__ == "__main__":
    """
input
-s sample_rate: 
-f flit_size

output
filename: trace_s_f_p_c.tr
p, c: num_packets, cycles
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('sample_rate', type=float)
    parser.add_argument('flit_size', type=int)

    args = parser.parse_args()
    sample_rate, flit_size = args.sample_rate, args.flit_size

    print("args:", args)

    exist_csvs = glob.glob("*.csv")
    print(exist_csvs[0])
    print(re.sub("_[0-9]*.csv$", "", exist_csvs[0]))
    traces = sorted(list(set([re.sub("_[0-9]*.csv$", "", exist_csv) for exist_csv in exist_csvs])))
    print(traces)

    for trace in traces:
        csvfiles = get_csvfiles(trace)
        purify_csv = PurifyCSV(csvfiles, sample_rate, flit_size)

        num_packets, num_cycles = purify_csv.get_num_packets_num_cycles()
        print("num_packets, num_cycles:", num_packets, num_cycles)
        
        # debugcount = 0
        # for clk, src, dst, packet_size in purify_csv.purify_csv():
        #     print(clk,src,dst,packet_size)
        #     debugcount += 1
        #     if debugcount > 100:
        #         exit(1)


        sample_rate_str = "{:.2e}".format(sample_rate).replace("+", "")
        outf_name = "{:s}_{:s}_{:d}_{:d}_{:d}.tr".format(trace, sample_rate_str, flit_size, num_packets, num_cycles)
        print("outf_name:", outf_name)

        with open(outf_name, 'w') as f:
            writer = csv.writer(f, delimiter=" ")
            writer.writerow([num_packets])
            for clk, src, dst, packet_size in purify_csv.purify_csv():
                if src != dst and packet_size > 0:
                    writer.writerow([clk, src, dst, packet_size])
