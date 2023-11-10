import csv
import argparse
import glob
import math
import subprocess
from collections import defaultdict as dd

def get_csvfiles(prefix):
    searching = "{:s}_[0-9]*.csv".format(prefix)
    # print(searching)
    csvfiles = glob.glob(searching)
    return sorted(csvfiles)

class EventPool:
    def __init__(self):
        self.events = list()
        self.counters = dd(int)

    def add_event(self, clk, src, dst, packet_size):
        if self.counters[src] < clk:
            self.events.append((clk,src,dst,packet_size))
            self.counters[src] = clk
        else:
            self.events.append((self.counters[src]+1,src,dst,packet_size))
            self.counters[src] += 1

    def get_countermax(self):
        return max(self.counters.values())

    def publish_events(self):
        for e in sorted(self.events):
            yield e
        self.events = list()
        self.counters = dd(int)

    def is_empty(self):
        return len(self.events) == 0

    def process_event(self, clk, src, dst, packet_size):
        if self.is_empty():
            self.add_event(clk, src, dst, packet_size)
        else:
            tmp_max = self.get_countermax()
            # print("tmp_max:", tmp_max)
            if tmp_max < clk:
                for e in self.publish_events():
                    yield e
            self.add_event(clk, src, dst, packet_size)

class PurifyCSV:
    def __init__(self, csvfiles, sample_rate, flit_size):
        self.csvfiles = csvfiles
        self.sample_rate = sample_rate
        self.flit_size = flit_size

    def get_num_packets_num_cycles(self):
        num_packets = 0
        num_cycles = 0
        for clk, src, dst, packet_size in self.purify_csv():
            if src != dst and packet_size > 0:
                num_packets += 1
                num_cycles = clk

        return num_packets, num_cycles

        # num_packets = 0
        # for csvfile in self.csvfiles:
        #     tmp_stdout = subprocess.run(["wc", "-l", csvfile], stdout = subprocess.PIPE).stdout.split()
        #     # print(tmp_stdout)
        #     num_lines = int(tmp_stdout[0])
        #     # print(num_lines)
        #     num_packets += num_lines
        #     # print("run:", subprocess.run(["wc", "-l", csvfile], stdout = subprocess.PIPE).stdout)
        # # print(num_packets)

        # tmp_stdout = subprocess.run(["tail", "-n1", csvfiles[-1]], stdout = subprocess.PIPE).stdout.decode("utf_8").split(",")
        # # print(tmp_stdout)
        # num_cycles = round(float(tmp_stdout[4]) * self.sample_rate)
        # # print(num_cycles)

        # return num_packets, num_cycles

    def purify_csv(self):
        event_pool = EventPool()

        is_head = True
        for csvfile in self.csvfiles:
            # print(csvfile)
            with open(csvfile) as f:
                reader = csv.reader(f)

                # test_counter = 0
                for row in reader:
                    if is_head:
                        is_head = False
                        continue
                    # print(row)
                    try:
                        src, dst, size, start = int(row[0][1:])-1, int(row[1][1:])-1, int(row[2]), float(row[4])
                    except:
                        import traceback
                        traceback.print_exc()
                        print(row)
                        exit(1)
                    # print(src, dst, size, start)
                    packet_size = math.ceil(size / self.flit_size)
                    clk = round(start * self.sample_rate)
                    # print(packet_size)
                    # print(clk)
                    if src != dst and packet_size > 0:
                        # print(event_pool.events)
                        for event in event_pool.process_event(clk, src, dst, packet_size):
                            yield event
                        # yield clk, src, dst, packet_size
                    # exit(1)

                    # test_counter += 1
                    # if test_counter > 100:
                    #     exit(1)

        if not event_pool.is_empty():
            for event in event_pool.publish_events():
                yield event

if __name__ == "__main__":
    """
input
-t trace: suffix (before _*.csv)
e.g.: crossbar_256_is.A.256_trace
-s sample_rate: 
-f flit_size

output
filename: trace_s_f_p_c.tr
p, c: num_packets, cycles
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('trace', help='trace file name prefix (before _*.csv)')
    parser.add_argument('sample_rate', type=float)
    parser.add_argument('flit_size', type=int)

    args = parser.parse_args()
    trace, sample_rate, flit_size = args.trace, args.sample_rate, args.flit_size

    print("args:", args)

    csvfiles = get_csvfiles(trace)
    print("csvfiles:", csvfiles)

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